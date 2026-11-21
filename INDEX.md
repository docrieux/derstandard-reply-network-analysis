# TFG: mapa del proyecto

Un experimento = una carpeta con el mismo nombre en `notes/experiments/` (documentación y resultados) y en `code/experiments/` (scripts). Nada vive en carpetas temporales.

```
tfg/
├── INDEX.md                      este mapa
├── data/derstandard/             dataset crudo y derived/ (~42 GB, fuera de git)
├── code/
│   ├── pyproject.toml            entorno uv compartido
│   ├── dataset-checks/           comprobaciones del dataset (duplicados, autovotos)
│   ├── experiments/              experimentos activos (vacío de momento)
│   └── _obsoleto/                código del diseño antiguo, guardado como registro
│       └── 01-reply-opposition-lifetime/   scripts 00…09 (+ common.py, plotstyle.py)
└── notes/                        vault de Obsidian
    ├── dataset/                  qué es el dataset: README, Codebook, descarga, tratamiento
    ├── method/                   cómo trabajo: uso de IA (AI-USE.md), diario de trabajo (WORKLOG.md)
    ├── experiments/
    │   ├── _template/            copiar para empezar un experimento nuevo
    │   └── 01-reply-opposition-lifetime/   README, PLAN, NOTES, RESULTS, results/
    ├── meetings/                 una nota por reunión
    ├── papers/                   PDFs de las lecturas
    └── templates/                plantillas de Obsidian
```

## Cómo empezar un experimento nuevo
1. Copiar `notes/experiments/_template/` a `notes/experiments/NN-nombre-corto/`.
2. Crear `code/experiments/NN-nombre-corto/` para los scripts. Los resultados se escriben en `notes/experiments/NN-nombre-corto/results/` (ver `RESULTS` en `common.py` del experimento 01).
3. Rellenar el README (pregunta + predicción) **antes** de escribir código.
4. Cada decisión metodológica va en el NOTES del experimento con su etiqueta `[me]` / `[AI, reviewed]` / `[AI, not yet reviewed]`. Las decisiones sobre limpieza de datos van en `notes/dataset/data-treatment.md`.

## Experimentos
| # | Nombre | Estado |
|---|---|---|
| 01 | [Respuestas, oposición y lifetime](notes/experiments/01-reply-opposition-lifetime/README.md) | diseño antiguo; código en `code/_obsoleto/` (2026-11-21). Planteamiento nuevo del 2026-11-19 en WORKLOG |
