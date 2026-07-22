"""Generate privacy-safe responsive image assets for the Jekyll site.

The original photography remains outside the repository. Run this script again
whenever one of the selected source files changes.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PHOTO_ROOT = Path(r"C:\Users\mauri\Documents\Marcenaria Mágica\Fotos")
SCREENSHOT_ROOT = Path(r"C:\Users\mauri\OneDrive\Pictures\Screenshots")
OUTPUT_ROOT = ROOT / "assets" / "images" / "generated"
MANIFEST_PATH = ROOT / "_data" / "media.json"
TARGET_WIDTHS = (480, 800, 1200, 1600)


MEDIA = {
    "projects/table-hero": (
        PHOTO_ROOT / "94202C84-DC26-44D7-B0C2-F21601EE2FC3.jpg",
        "Mesa de madeira maciça com veios marcantes e base metálica preta.",
    ),
    "projects/kitchen-white-wood-wide": (
        PHOTO_ROOT / "IMG_20211221_180941453.jpg",
        "Vista ampla de cozinha compacta com armários brancos e nichos em madeira.",
    ),
    "projects/kitchen-white-wood-hero": (
        PHOTO_ROOT / "IMG_20211221_180941453.jpg",
        "Cozinha compacta com marcenaria branca, puxadores e nichos em madeira.",
    ),
    "projects/kitchen-white-wood-angle": (
        PHOTO_ROOT / "IMG_20211221_180904489.jpg",
        "Cozinha sob medida com marcenaria branca, puxadores e nichos em madeira.",
    ),
    "projects/kitchen-white-wood-detail": (
        PHOTO_ROOT / "IMG_20211221_180926123.jpg",
        "Torre de cozinha com armários brancos, nichos de madeira e espaço para micro-ondas.",
    ),
    "projects/modular-workstation-open-a": (
        PHOTO_ROOT / "IMG_20210621_125139654_HDR.jpg",
        "Estação modular branca com superfícies retráteis abertas sob as janelas.",
    ),
    "projects/modular-workstation-open-b": (
        PHOTO_ROOT / "IMG_20210621_125155528_HDR.jpg",
        "Vista lateral da estação de trabalho modular com tampos deslizantes.",
    ),
    "projects/modular-workstation-closed": (
        PHOTO_ROOT / "IMG_20210922_164422373.jpg",
        "Estação modular fechada formando um móvel baixo e contínuo.",
    ),
    "projects/compact-kitchen-2020": (
        PHOTO_ROOT / "IMG_20200918_134456803.jpg",
        "Armários inferiores cinza-claro feitos sob medida para uma cozinha compacta.",
    ),
    "projects/kitchen-upper-lower": (
        SCREENSHOT_ROOT / "Captura de tela 2026-07-22 143051.png",
        "Cozinha com armários superiores brancos e inferiores com acabamento amadeirado.",
    ),
    "projects/kitchen-white-countertop": (
        SCREENSHOT_ROOT / "Captura de tela 2026-07-22 143121.png",
        "Cozinha branca sob medida com bancada contínua de madeira.",
    ),
    "projects/bathroom-shelf": (
        SCREENSHOT_ROOT / "Captura de tela 2026-07-22 143141.png",
        "Prateleira de madeira com porta-papel integrada.",
    ),
    "decor/landscape-wide": (
        PHOTO_ROOT / "4CE08FB6-EA3C-4E18-A248-6A4C70332A6B.jpg",
        "Quadro autoral em madeira representando montanhas e um teleférico.",
    ),
    "decor/landscape-detail": (
        PHOTO_ROOT / "0637AD2D-96C3-42C8-B212-C061491FA1F3.jpg",
        "Detalhe do relevo, dos veios da madeira e do teleférico gravado no quadro.",
    ),
    "decor/landscape-alt": (
        PHOTO_ROOT / "Screenshot_20260529_121458_Photos.jpg",
        "Paisagem de montanha composta em madeira clara e escura.",
    ),
    "decor/cat-house-plants": (
        PHOTO_ROOT / "3db2315d-8c8b-40ab-81ed-d81d1f9edb8b.jpg",
        "Casinha de madeira para gatos usada também como apoio para um vaso.",
    ),
    "decor/cat-house-portrait": (
        PHOTO_ROOT / "eefd4d14-2231-404a-81f5-050e76779f0c.jpg",
        "Gato acomodado na abertura circular de sua casinha de madeira.",
    ),
    "decor/board-knife": (
        PHOTO_ROOT / "IMG_20201128_115909544_HDR.jpg",
        "Tábua artesanal de madeira com faca apoiada sobre os veios naturais.",
    ),
    "decor/board-bread-top": (
        PHOTO_ROOT / "IMG_20201128_120308589_HDR.jpg",
        "Pão fatiado sobre uma tábua artesanal de madeira.",
    ),
    "decor/board-bread-angle": (
        PHOTO_ROOT / "IMG_20201128_120319102.jpg",
        "Vista baixa da tábua artesanal com bordas arredondadas.",
    ),
    "decor/candle-holder-wide": (
        PHOTO_ROOT / "IMG_20210612_160746233.jpg",
        "Porta-velas linear de madeira com três velas.",
    ),
    "decor/candle-holder-detail": (
        PHOTO_ROOT / "IMG_20210612_160810376.jpg",
        "Detalhe dos encaixes e veios de um porta-velas de madeira.",
    ),
    "decor/pet-feeder-wood": (
        PHOTO_ROOT / "IMG_20211110_160801331.jpg",
        "Comedouro elevado de madeira clara com dois recipientes de inox.",
    ),
    "decor/pet-feeder-white": (
        PHOTO_ROOT / "IMG_20211123_111124_417.jpg",
        "Comedouro elevado branco com dois recipientes de inox.",
    ),
    "decor/serving-stands-front": (
        PHOTO_ROOT / "b0efc067-529a-4b13-b455-bc3225380126.jpg",
        "Dois suportes baixos de madeira para servir ou expor objetos.",
    ),
    "decor/serving-stands-angle": (
        PHOTO_ROOT / "fc40bbac-2e3f-4bcc-aa70-6afec2b1eb91.jpg",
        "Vista em perspectiva de suportes baixos feitos em madeira.",
    ),
    "decor/tree-natural-close": (
        PHOTO_ROOT / "C47589A9-813E-485A-B853-9002BB7C509C.jpg",
        "Árvore de Natal minimalista feita em madeira natural.",
    ),
    "decor/trees-group": (
        PHOTO_ROOT / "CB3F5C26-85B4-496E-87C7-3B2BF2258911.jpg",
        "Três árvores de Natal de madeira em acabamentos natural, branco e verde.",
    ),
    "decor/tree-decorated": (
        PHOTO_ROOT / "FBA1BFD8-CF7F-4313-A838-D18478D94075.jpg",
        "Árvore de Natal de madeira natural com pequenos enfeites pendurados.",
    ),
    "about/mauricio-work": (
        PHOTO_ROOT / "IMG_20171211_095258_765.jpg",
        "Mauricio trabalhando a madeira com uma ferramenta manual durante o curso de marcenaria fina.",
    ),
    "about/course-collaboration": (
        PHOTO_ROOT / "IMG_20171126_163524_602.jpg",
        "Mauricio e um colega prendendo peças de madeira durante o curso.",
    ),
    "about/final-table": (
        PHOTO_ROOT / "IMG_20171211_201017_326.jpg",
        "Mauricio fotografando a mesa de centro concluída no curso de marcenaria fina.",
    ),
    "about/final-table-affection": (
        PHOTO_ROOT / "IMG_20171211_201017_327.jpg",
        "Mauricio abraçando com bom humor a mesa de centro que construiu.",
    ),
    "about/wood-selection": (
        PHOTO_ROOT / "IMG_20171014_085527940.jpg",
        "Pranchas de diferentes espécies de madeira selecionadas para o curso.",
    ),
}

SPECIAL_CROPS = {
    # Removes the refrigerator and personal objects from the public page hero.
    "projects/kitchen-white-wood-hero": (0.42, 0.0, 1.0, 1.0),
}


def output_widths(source_width: int) -> list[int]:
    widths = [width for width in TARGET_WIDTHS if width < source_width]
    widths.append(source_width if source_width < TARGET_WIDTHS[-1] else TARGET_WIDTHS[-1])
    return sorted(set(widths))


def process_image(key: str, source: Path, alt: str) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)

    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        if key in SPECIAL_CROPS:
            left, top, right, bottom = SPECIAL_CROPS[key]
            width, height = image.size
            image = image.crop(
                (
                    round(width * left),
                    round(height * top),
                    round(width * right),
                    round(height * bottom),
                )
            )
        source_width, source_height = image.size
        variants = []

        for width in output_widths(source_width):
            height = round(source_height * width / source_width)
            resized = image.resize((width, height), Image.Resampling.LANCZOS)
            stem = OUTPUT_ROOT / f"{key}-{width}"
            stem.parent.mkdir(parents=True, exist_ok=True)

            paths = {
                "avif": stem.with_suffix(".avif"),
                "webp": stem.with_suffix(".webp"),
                "jpg": stem.with_suffix(".jpg"),
            }
            if not paths["avif"].exists():
                resized.save(paths["avif"], "AVIF", quality=52, speed=8)
            if not paths["webp"].exists():
                resized.save(paths["webp"], "WEBP", quality=78, method=6)
            if not paths["jpg"].exists():
                resized.save(paths["jpg"], "JPEG", quality=82, optimize=True, progressive=True)

            variants.append(
                {
                    "width": width,
                    "height": height,
                    **{
                        fmt: "/" + path.relative_to(ROOT).as_posix()
                        for fmt, path in paths.items()
                    },
                }
            )

    return {
        "alt": alt,
        "width": variants[-1]["width"],
        "height": variants[-1]["height"],
        "variants": variants,
        "fallback": variants[-1]["jpg"],
    }


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for key, (source, alt) in MEDIA.items():
        print(f"Processing {key} <- {source.name}")
        manifest[key] = process_image(key, source, alt)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(manifest)} media entries to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
