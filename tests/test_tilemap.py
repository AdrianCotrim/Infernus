from pathlib import Path

import pytest

from tilemap import Tilemap, TilemapError, TilesetMetadata, load_csv_layer


def write_csv(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_load_csv_layer_preserves_rows_columns_and_values(tmp_path):
    path = write_csv(tmp_path, "ground.csv", "0,1,2\n3,4,5\n")

    assert load_csv_layer(path) == ((0, 1, 2), (3, 4, 5))


def test_tilemap_identifies_empty_cells_and_queries_bounds():
    tilemap = Tilemap(layers={"ground": ((0, 5), (6, 0))})

    assert tilemap.is_empty("ground", 0, 0)
    assert not tilemap.is_empty("ground", 1, 0)
    assert tilemap.cell("ground", 2, 0) is None
    assert tilemap.cell("ground", -1, 0) is None


def test_csv_errors_include_path_and_problem(tmp_path):
    missing = tmp_path / "missing.csv"
    empty = write_csv(tmp_path, "empty.csv", "")
    invalid = write_csv(tmp_path, "invalid.csv", "1,x\n")
    uneven = write_csv(tmp_path, "uneven.csv", "1,2\n3\n")

    with pytest.raises(TilemapError, match="missing.csv"):
        load_csv_layer(missing)
    with pytest.raises(TilemapError, match="vazio"):
        load_csv_layer(empty)
    with pytest.raises(TilemapError, match="linha 1"):
        load_csv_layer(invalid)
    with pytest.raises(TilemapError, match="largura inconsistente"):
        load_csv_layer(uneven)


def test_layer_dimensions_can_be_validated():
    tilemap = Tilemap(
        layers={
            "background": ((1, 2), (3, 4)),
            "collision": ((0, 1), (1, 0)),
        }
    )

    assert tilemap.layer_size("background") == (2, 2)
    assert tilemap.validate_dimensions() == (2, 2)

    tilemap.add_layer("foreground", ((1,),))
    with pytest.raises(TilemapError, match="Dimensões incompatíveis"):
        tilemap.validate_dimensions()


def test_tiled_gid_is_converted_to_local_tile_id():
    metadata = TilesetMetadata(
        first_gid=17,
        tile_count=8,
        columns=4,
        tile_width=16,
        tile_height=16,
    )

    assert metadata.local_tile_id(0) is None
    assert metadata.local_tile_id(17) == 0
    assert metadata.local_tile_id(20) == 3
    assert metadata.source_rect(20).topleft == (48, 0)
    with pytest.raises(TilemapError, match="não pertence"):
        metadata.local_tile_id(25)
