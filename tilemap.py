"""Dados e carregamento de camadas CSV exportadas pelo Tiled."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator, Mapping, Sequence


class TilemapError(ValueError):
    """Erro de formato ou configuração de um tilemap."""


def load_csv_layer(path: str | Path) -> tuple[tuple[int, ...], ...]:
    """Carrega uma camada CSV retangular, preservando os GIDs do Tiled."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise TilemapError(f"Arquivo de camada não encontrado: {csv_path}")

    try:
        with csv_path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.reader(file))
    except OSError as error:
        raise TilemapError(
            f"Não foi possível ler a camada '{csv_path}': {error}"
        ) from error

    if not rows or all(not row for row in rows):
        raise TilemapError(f"Arquivo de camada vazio: {csv_path}")

    width = len(rows[0])
    if width == 0:
        raise TilemapError(f"Arquivo de camada vazio: {csv_path}")

    values: list[tuple[int, ...]] = []
    for line_number, row in enumerate(rows, start=1):
        if len(row) != width:
            raise TilemapError(
                f"Camada '{csv_path}' possui largura inconsistente na linha "
                f"{line_number}: esperadas {width} colunas, encontradas {len(row)}"
            )

        parsed_row: list[int] = []
        for column_number, value in enumerate(row, start=1):
            text = value.strip()
            try:
                parsed_row.append(int(text))
            except ValueError as error:
                raise TilemapError(
                    f"Valor inválido na camada '{csv_path}', linha "
                    f"{line_number}, coluna {column_number}: {value!r}"
                ) from error
        values.append(tuple(parsed_row))

    return tuple(values)


class TilesetMetadata:
    """Metadados necessários para converter GIDs globais em IDs locais."""

    def __init__(
        self,
        first_gid: int,
        tile_count: int,
        columns: int,
        tile_width: int,
        tile_height: int,
        spacing: int = 0,
        margin: int = 0,
    ):
        if first_gid < 1:
            raise TilemapError("first_gid do tileset deve ser maior ou igual a 1")
        if tile_count < 1 or columns < 1:
            raise TilemapError("tile_count e columns devem ser maiores que zero")
        if tile_width < 1 or tile_height < 1:
            raise TilemapError("As dimensões dos tiles devem ser maiores que zero")
        if spacing < 0 or margin < 0:
            raise TilemapError("spacing e margin não podem ser negativos")

        self.first_gid = first_gid
        self.tile_count = tile_count
        self.columns = columns
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.spacing = spacing
        self.margin = margin

    @property
    def last_gid(self) -> int:
        return self.first_gid + self.tile_count - 1

    def contains_gid(self, gid: int) -> bool:
        return self.first_gid <= gid <= self.last_gid

    def local_tile_id(self, gid: int) -> int | None:
        """Converte um GID global Tiled em um ID local zero-based."""
        if gid == 0:
            return None
        if not self.contains_gid(gid):
            raise TilemapError(
                f"GID {gid} não pertence ao tileset iniciado em {self.first_gid}"
            )
        return gid - self.first_gid

    def source_rect(self, gid: int):
        """Retorna o recorte do tile no tileset, sem tratar GID como coordenada."""
        import pygame

        local_id = self.local_tile_id(gid)
        if local_id is None:
            return None
        column = local_id % self.columns
        row = local_id // self.columns
        x = self.margin + column * (self.tile_width + self.spacing)
        y = self.margin + row * (self.tile_height + self.spacing)
        return pygame.Rect(x, y, self.tile_width, self.tile_height)


class Tilemap:
    """Representação independente da janela e do Pygame para um mapa em grade."""

    def __init__(
        self,
        tile_size: tuple[int, int] = (32, 32),
        layers: Mapping[str, Sequence[Sequence[int]]] | None = None,
    ):
        if len(tile_size) != 2 or tile_size[0] < 1 or tile_size[1] < 1:
            raise TilemapError("tile_size deve conter largura e altura positivas")
        self.tile_size = (int(tile_size[0]), int(tile_size[1]))
        self._layers: dict[str, tuple[tuple[int, ...], ...]] = {}
        if layers:
            for name, data in layers.items():
                self.add_layer(name, data)

    @property
    def layers(self) -> tuple[str, ...]:
        return tuple(self._layers)

    def add_layer(
        self,
        name: str,
        data: Sequence[Sequence[int]],
    ) -> None:
        if not name:
            raise TilemapError("O nome da camada não pode ser vazio")
        rows = tuple(tuple(int(value) for value in row) for row in data)
        if not rows or not rows[0]:
            raise TilemapError(f"Camada '{name}' vazia")
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise TilemapError(f"Camada '{name}' possui linhas com larguras diferentes")
        self._layers[name] = rows

    def add_csv_layer(self, name: str, path: str | Path) -> None:
        self.add_layer(name, load_csv_layer(path))

    def layer_size(self, name: str) -> tuple[int, int]:
        layer = self._get_layer(name)
        return len(layer[0]), len(layer)

    def cell(self, layer_name: str, column: int, row: int) -> int | None:
        """Retorna o GID da célula; None indica coordenada fora da camada."""
        layer = self._get_layer(layer_name)
        if row < 0 or row >= len(layer) or column < 0 or column >= len(layer[row]):
            return None
        return layer[row][column]

    def is_empty(self, layer_name: str, column: int, row: int) -> bool:
        """Células com GID 0 são vazias; fora do mapa também não contém tile."""
        value = self.cell(layer_name, column, row)
        return value is None or value == 0

    def validate_dimensions(self, layer_names: Sequence[str] | None = None) -> tuple[int, int]:
        names = tuple(layer_names) if layer_names is not None else self.layers
        if not names:
            raise TilemapError("Nenhuma camada foi informada para validação")
        expected = self.layer_size(names[0])
        for name in names[1:]:
            actual = self.layer_size(name)
            if actual != expected:
                raise TilemapError(
                    f"Dimensões incompatíveis entre camadas: '{names[0]}' "
                    f"{expected[0]}x{expected[1]} e '{name}' "
                    f"{actual[0]}x{actual[1]}"
                )
        return expected

    def iter_cells(self, layer_name: str) -> Iterator[tuple[int, int, int]]:
        layer = self._get_layer(layer_name)
        for row, values in enumerate(layer):
            for column, gid in enumerate(values):
                yield column, row, gid

    def _get_layer(self, name: str) -> tuple[tuple[int, ...], ...]:
        try:
            return self._layers[name]
        except KeyError as error:
            raise TilemapError(f"Camada inexistente: '{name}'") from error
