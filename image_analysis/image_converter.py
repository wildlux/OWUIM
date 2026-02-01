#!/usr/bin/env python3
"""
Image Converter per Open WebUI
Converte PNG/SVG in formato compatibile con Open WebUI (evita bug base64 loop)

Autore: Carlo
Versione: 1.0.0

Uso standalone:
    python image_converter.py immagine.png
    python image_converter.py immagine.svg

Uso programmatico:
    from image_converter import ImageConverter
    converter = ImageConverter()
    result = converter.convert_file("immagine.png")
"""

import sys
import os
import base64
import io
import argparse
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False


class ImageConverter:
    """Convertitore immagini per compatibilità Open WebUI."""

    # Limiti per evitare il bug del loop ciclico
    MAX_BASE64_LENGTH = 40000  # caratteri
    MAX_DIMENSION = 800  # pixel
    DEFAULT_QUALITY = 70  # JPEG quality

    def __init__(self, max_dimension: int = 800, quality: int = 70):
        self.max_dimension = max_dimension
        self.quality = quality

    def convert_svg_to_png(self, svg_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Converte SVG in PNG.

        Args:
            svg_path: Percorso file SVG
            output_path: Percorso output (opzionale, default: stesso nome .png)

        Returns:
            (successo, messaggio/percorso)
        """
        if not HAS_CAIRO:
            # Fallback: prova con Inkscape
            return self._convert_svg_inkscape(svg_path, output_path)

        try:
            if not output_path:
                output_path = str(Path(svg_path).with_suffix('.png'))

            cairosvg.svg2png(
                url=svg_path,
                write_to=output_path,
                output_width=self.max_dimension
            )

            return True, output_path

        except Exception as e:
            return False, f"Errore conversione SVG: {e}"

    def _convert_svg_inkscape(self, svg_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Fallback: usa Inkscape per convertire SVG."""
        import subprocess
        import shutil

        if not shutil.which("inkscape"):
            return False, "Installa cairosvg (pip install cairosvg) o Inkscape per convertire SVG"

        try:
            if not output_path:
                output_path = str(Path(svg_path).with_suffix('.png'))

            subprocess.run([
                "inkscape",
                svg_path,
                "--export-type=png",
                f"--export-filename={output_path}",
                f"--export-width={self.max_dimension}"
            ], check=True, capture_output=True)

            return True, output_path

        except subprocess.CalledProcessError as e:
            return False, f"Errore Inkscape: {e.stderr.decode()}"

    def compress_image(self, image_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Comprime e ridimensiona un'immagine per compatibilità Open WebUI.

        Args:
            image_path: Percorso immagine (PNG, JPEG, etc.)
            output_path: Percorso output (opzionale)

        Returns:
            (successo, messaggio/percorso)
        """
        if not HAS_PIL:
            return False, "Pillow non installato. Esegui: pip install Pillow"

        try:
            img = Image.open(image_path)

            # Ridimensiona se troppo grande
            if max(img.size) > self.max_dimension:
                ratio = self.max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Converti in RGB per JPEG
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA' or img.mode == 'LA':
                    # Gestisci trasparenza
                    if img.mode == 'LA':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Salva come JPEG compresso
            if not output_path:
                output_path = str(Path(image_path).with_suffix('.jpg'))

            img.save(output_path, 'JPEG', quality=self.quality, optimize=True)

            return True, output_path

        except Exception as e:
            return False, f"Errore compressione: {e}"

    def to_base64(self, image_path: str, check_size: bool = True) -> Tuple[bool, str]:
        """
        Converte immagine in base64 compatibile con Open WebUI.

        Se l'immagine è troppo grande, la comprime automaticamente.

        Args:
            image_path: Percorso immagine
            check_size: Verifica e comprime se necessario

        Returns:
            (successo, base64_string o messaggio errore)
        """
        if not HAS_PIL:
            return False, "Pillow non installato. Esegui: pip install Pillow"

        try:
            path = Path(image_path)

            # Se SVG, prima converti in PNG
            if path.suffix.lower() == '.svg':
                success, result = self.convert_svg_to_png(str(path))
                if not success:
                    return False, result
                image_path = result

            # Apri immagine
            img = Image.open(image_path)
            original_size = img.size

            # Ridimensiona se necessario
            if max(img.size) > self.max_dimension:
                ratio = self.max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Prova prima come PNG
            buf = io.BytesIO()
            img.save(buf, format='PNG', optimize=True)
            png_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            # Se troppo grande, usa JPEG
            if len(png_base64) > self.MAX_BASE64_LENGTH:
                # Converti in RGB
                if img.mode in ('RGBA', 'P', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode in ('RGBA', 'LA'):
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Comprimi come JPEG
                quality = self.quality
                while quality >= 30:
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=quality, optimize=True)
                    jpeg_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

                    if len(jpeg_base64) <= self.MAX_BASE64_LENGTH:
                        return True, f"data:image/jpeg;base64,{jpeg_base64}"

                    quality -= 10

                # Ancora troppo grande? Riduci dimensioni
                while max(img.size) > 200:
                    img = img.resize((img.size[0] // 2, img.size[1] // 2), Image.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=50, optimize=True)
                    jpeg_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

                    if len(jpeg_base64) <= self.MAX_BASE64_LENGTH:
                        return True, f"data:image/jpeg;base64,{jpeg_base64}"

                return False, "Impossibile comprimere l'immagine a dimensioni compatibili"

            return True, f"data:image/png;base64,{png_base64}"

        except Exception as e:
            return False, f"Errore conversione base64: {e}"

    def convert_file(self, input_path: str, output_format: str = "base64") -> dict:
        """
        Converte un file immagine.

        Args:
            input_path: Percorso file input
            output_format: "base64", "jpeg", "png"

        Returns:
            Dict con risultato
        """
        path = Path(input_path)

        if not path.exists():
            return {"success": False, "error": f"File non trovato: {input_path}"}

        if not HAS_PIL:
            return {"success": False, "error": "Pillow non installato"}

        result = {
            "success": False,
            "input": str(path),
            "input_size": path.stat().st_size,
            "format": output_format
        }

        try:
            if output_format == "base64":
                success, data = self.to_base64(str(path))
                if success:
                    result["success"] = True
                    result["base64"] = data
                    result["base64_length"] = len(data)
                    result["compatible"] = len(data) <= self.MAX_BASE64_LENGTH
                else:
                    result["error"] = data

            elif output_format in ("jpeg", "jpg"):
                output_path = str(path.with_suffix('.jpg'))
                success, data = self.compress_image(str(path), output_path)
                if success:
                    result["success"] = True
                    result["output"] = data
                    result["output_size"] = Path(data).stat().st_size
                else:
                    result["error"] = data

            elif output_format == "png":
                if path.suffix.lower() == '.svg':
                    success, data = self.convert_svg_to_png(str(path))
                    if success:
                        result["success"] = True
                        result["output"] = data
                        result["output_size"] = Path(data).stat().st_size
                    else:
                        result["error"] = data
                else:
                    result["success"] = True
                    result["output"] = str(path)
                    result["note"] = "File già in formato PNG"

            else:
                result["error"] = f"Formato non supportato: {output_format}"

        except Exception as e:
            result["error"] = str(e)

        return result


def main():
    """Entry point CLI."""
    parser = argparse.ArgumentParser(
        description="Converte immagini per compatibilità Open WebUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python image_converter.py immagine.png              # Converte in base64
  python image_converter.py immagine.svg -f jpeg     # SVG -> JPEG
  python image_converter.py immagine.png -f jpeg -q 50   # PNG -> JPEG quality 50
  python image_converter.py immagine.svg -f png      # SVG -> PNG
  python image_converter.py *.png --batch            # Converte tutti i PNG
"""
    )

    parser.add_argument("files", nargs="+", help="File da convertire")
    parser.add_argument("-f", "--format", choices=["base64", "jpeg", "png"],
                        default="base64", help="Formato output (default: base64)")
    parser.add_argument("-q", "--quality", type=int, default=70,
                        help="Qualità JPEG 1-100 (default: 70)")
    parser.add_argument("-s", "--size", type=int, default=800,
                        help="Dimensione massima in pixel (default: 800)")
    parser.add_argument("--batch", action="store_true",
                        help="Modalità batch (più file)")
    parser.add_argument("-o", "--output", help="Directory output (per batch)")
    parser.add_argument("-c", "--copy", action="store_true",
                        help="Copia base64 negli appunti")

    args = parser.parse_args()

    if not HAS_PIL:
        print("ERRORE: Pillow non installato")
        print("Esegui: pip install Pillow")
        sys.exit(1)

    converter = ImageConverter(max_dimension=args.size, quality=args.quality)

    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"[X] File non trovato: {file_path}")
            continue

        print(f"\n[*] Elaborazione: {path.name}")
        print(f"    Dimensione: {path.stat().st_size / 1024:.1f} KB")

        result = converter.convert_file(str(path), args.format)

        if result["success"]:
            if args.format == "base64":
                print(f"[OK] Base64 generato ({result['base64_length']:,} caratteri)")

                if result.get("compatible"):
                    print("    Compatibile con Open WebUI")
                else:
                    print("    ATTENZIONE: Potrebbe causare problemi")

                if args.copy:
                    try:
                        import pyperclip
                        pyperclip.copy(result["base64"])
                        print("    Copiato negli appunti!")
                    except ImportError:
                        print("    (pip install pyperclip per copiare negli appunti)")

                # Mostra anteprima HTML
                preview_file = path.with_suffix('.html')
                with open(preview_file, 'w') as f:
                    f.write(f"""<!DOCTYPE html>
<html>
<head><title>Preview: {path.name}</title></head>
<body style="background:#222; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0;">
<img src="{result['base64']}" style="max-width:90%; max-height:90vh;">
</body>
</html>""")
                print(f"    Preview HTML: {preview_file}")

            else:
                output_size = result.get("output_size", 0)
                reduction = (1 - output_size / result["input_size"]) * 100 if output_size else 0
                print(f"[OK] Salvato: {result['output']}")
                print(f"    Nuovo size: {output_size / 1024:.1f} KB (-{reduction:.0f}%)")

        else:
            print(f"[X] Errore: {result.get('error', 'Sconosciuto')}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
