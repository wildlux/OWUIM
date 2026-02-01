# Document Reader Service

Servizio locale per leggere documenti di vari formati e restituire testo/JSON utilizzabile da LLM.

## Porta

`5557`

## Formati Supportati

### Documenti Office
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| PDF | .pdf | pypdf |
| Word | .docx | python-docx |
| Word (legacy) | .doc | LibreOffice |
| Excel | .xlsx | openpyxl |
| Excel (legacy) | .xls | LibreOffice |
| PowerPoint | .pptx | python-pptx |
| PowerPoint (legacy) | .ppt | LibreOffice |
| Rich Text | .rtf | LibreOffice |
| WordPerfect | .wpd | LibreOffice |
| Microsoft Works | .wps | LibreOffice |

### LibreOffice / OpenDocument
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| OpenDocument Text | .odt | LibreOffice |
| OpenDocument Spreadsheet | .ods | LibreOffice |
| OpenDocument Presentation | .odp | LibreOffice |
| OpenDocument Graphics | .odg | LibreOffice |
| OpenDocument Formula | .odf | LibreOffice |
| OpenDocument Database | .odb | LibreOffice |
| Flat ODF (Text, Spreadsheet, Presentation) | .fodt, .fods, .fodp | LibreOffice |
| Templates | .ott, .ots, .otp, .otg | LibreOffice |

### E-book
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| EPUB | .epub | ebooklib |
| Kindle | .mobi, .azw, .azw3 | Calibre |
| FictionBook | .fb2 | Calibre |

### Immagini GIMP / Editor grafici
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| GIMP | .xcf | GIMP o ImageMagick |
| Photoshop | .psd, .psb | GIMP o ImageMagick |
| OpenRaster | .ora | GIMP o ImageMagick |
| Krita | .kra, .krz | GIMP o ImageMagick |
| Adobe Illustrator | .ai | GIMP o ImageMagick |
| Encapsulated PostScript | .eps | GIMP o ImageMagick |

### Immagini Standard
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| PNG | .png | Pillow |
| JPEG | .jpg, .jpeg | Pillow |
| GIF | .gif | Pillow |
| BMP | .bmp | Pillow |
| TIFF | .tiff, .tif | Pillow |
| WebP | .webp | Pillow |
| ICO | .ico, .icns | Pillow |
| PPM/PGM/PBM | .ppm, .pgm, .pbm | Pillow |
| PCX | .pcx | Pillow |
| TGA | .tga | Pillow |
| OpenEXR | .exr | Pillow |
| HDR | .hdr | Pillow |
| DDS | .dds | Pillow |

### Immagini RAW (fotocamere)
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| Canon | .cr2, .cr3 | rawpy o ImageMagick |
| Nikon | .nef, .nrw | rawpy o ImageMagick |
| Sony | .arw | rawpy o ImageMagick |
| Olympus | .orf | rawpy o ImageMagick |
| Panasonic | .rw2 | rawpy o ImageMagick |
| Pentax | .pef | rawpy o ImageMagick |
| Fujifilm | .raf | rawpy o ImageMagick |
| Samsung | .srw | rawpy o ImageMagick |
| Sigma | .x3f | rawpy o ImageMagick |
| Digital Negative | .dng | rawpy o ImageMagick |
| Generic RAW | .raw | rawpy o ImageMagick |

### Vettoriali
| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| SVG | .svg, .svgz | cairosvg o Inkscape |
| Windows Metafile | .wmf, .emf | LibreOffice |
| CorelDRAW | .cdr | LibreOffice |

### Testo e Markup
| Formato | Estensione |
|---------|------------|
| Plain Text | .txt |
| Markdown | .md |
| CSV/TSV | .csv, .tsv |
| JSON | .json, .geojson, .jsonl |
| XML | .xml |
| HTML/XHTML | .html, .htm, .xhtml |
| LaTeX | .tex, .latex |
| reStructuredText | .rst |
| AsciiDoc | .asciidoc, .adoc |
| YAML | .yaml, .yml |
| TOML | .toml |
| INI/Config | .ini, .cfg, .conf, .properties |

### Codice Sorgente (60+ linguaggi)
Python, JavaScript, TypeScript, Java, Kotlin, Scala, C, C++, C#, F#, Visual Basic, Go, Rust, Ruby, PHP, Perl, Swift, Objective-C, R, Julia, Lua, Dart, Elm, Elixir, Erlang, Clojure, Haskell, OCaml, Nim, Zig, D, Pascal, Assembly, CoffeeScript, Vue.js, Svelte, CSS/SCSS/SASS/Less, SQL, GraphQL, Protocol Buffers, Terraform, Dockerfile, Makefile, e altri.

## Installazione

### Dipendenze Base (obbligatorie)
```bash
pip install fastapi uvicorn python-multipart
```

### Lettori Documenti (consigliati)
```bash
pip install pypdf python-docx openpyxl python-pptx
```

### Immagini
```bash
pip install Pillow  # Immagini standard

# RAW (opzionale)
pip install rawpy

# SVG (opzionale, uno dei due)
pip install cairosvg
# oppure installa Inkscape
```

### E-book
```bash
pip install ebooklib beautifulsoup4  # EPUB

# Per altri formati e-book
sudo apt install calibre  # Linux
# o scarica da https://calibre-ebook.com/
```

### Per formati avanzati (opzionali)
```bash
# LibreOffice (per .doc, .xls, .ppt, .odt, .ods, etc.)
sudo apt install libreoffice  # Linux

# GIMP (per .xcf, .psd, .ora)
sudo apt install gimp  # Linux

# ImageMagick (alternativa a GIMP per immagini)
sudo apt install imagemagick  # Linux
```

## Avvio

### Linux
```bash
cd document_service
chmod +x start_document_service.sh
./start_document_service.sh
```

### Windows
```batch
cd document_service
start_document_service.bat
```

## API Endpoints

### `GET /`
Health check e informazioni servizio.

### `GET /formats`
Lista tutti i formati supportati con stato disponibilità.

### `POST /read`
Legge documento e restituisce contenuto strutturato.

```bash
# PDF
curl -X POST -F "file=@documento.pdf" http://localhost:5557/read

# Immagine GIMP
curl -X POST -F "file=@progetto.xcf" http://localhost:5557/read

# E-book
curl -X POST -F "file=@libro.epub" http://localhost:5557/read
```

### `POST /extract-text`
Estrae solo il testo dal documento.

### `POST /get-metadata`
Restituisce solo i metadati (senza contenuto testuale).

### `POST /summary`
Restituisce un riassunto breve del documento.

### `POST /batch`
Legge multiple documenti in batch.

### `DELETE /cache`
Pulisce la cache dei documenti.

## Integrazione con Open WebUI

Usa il tool `tools/document_reader.py` per integrare questo servizio con Open WebUI.

## Troubleshooting

### "LibreOffice non installato"
```bash
# Linux
sudo apt install libreoffice

# Windows
winget install TheDocumentFoundation.LibreOffice
```

### "GIMP non installato"
```bash
# Linux
sudo apt install gimp

# Windows
winget install GIMP.GIMP

# Alternativa: usa ImageMagick
sudo apt install imagemagick  # Linux
winget install ImageMagick.ImageMagick  # Windows
```

### "rawpy non installato"
```bash
pip install rawpy

# Se fallisce, usa ImageMagick come fallback
```

### "Calibre non installato"
```bash
# Linux
sudo apt install calibre

# Windows
winget install calibre.calibre
```

## Note

- Max file size: 50MB (configurabile)
- Cache: 24 ore
- Per immagini con testo usa Image Analysis Service (porta 5555) con OCR
