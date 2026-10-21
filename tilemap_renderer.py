"""Renderização opcional de camadas de um :mod:`tilemap` usando Pygame."""

from __future__ import annotations

from pathlib import Path

import pygame

from tilemap import Tilemap, TilemapError, TilesetMetadata


class Tileset:
    """Imagem e metadados de um tileset exportado pelo Tiled."""

    def __init__(self, image: pygame.Surface, metadata: TilesetMetadata):
        self.image = image
        self.metadata = metadata

    @classmethod
    def from_file(cls, path: str | Path, metadata: TilesetMetadata) -> "Tileset":
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, OSError) as error:
            raise TilemapError(
                f"Não foi possível carregar o tileset '{path}': {error}"
            ) from error
        return cls(image, metadata)


class TilemapRenderer:
    """Desenha uma camada sem alterar a representação ou a lógica do mapa."""

    def draw_layer(
        self,
        target: pygame.Surface,
        tilemap: Tilemap,
        layer_name: str,
        tileset: Tileset,
        camera_rect: pygame.Rect | None = None,
    ) -> None:
        tile_width, tile_height = tilemap.tile_size
        visible = camera_rect or pygame.Rect(
            0,
            0,
            target.get_width(),
            target.get_height(),
        )
        for column, row, gid in tilemap.iter_cells(layer_name):
            if gid == 0:
                continue
            world_rect = pygame.Rect(
                column * tile_width,
                row * tile_height,
                tile_width,
                tile_height,
            )
            if not world_rect.colliderect(visible):
                continue
            source_rect = tileset.metadata.source_rect(gid)
            if source_rect is None:
                continue
            destination = world_rect.move(-visible.left, -visible.top)
            target.blit(tileset.image, destination, source_rect)
