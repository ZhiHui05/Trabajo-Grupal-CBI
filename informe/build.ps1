# Genera la memoria a partir de informe/secciones/*.md con pandoc.
# Uso (desde cualquier carpeta):  .\informe\build.ps1
# Salida: informe/build/Memoria_Grupo_CBI.pdf (o .docx si no hay motor LaTeX).
# Titulo, idioma y margenes: informe/metadata.yaml

$ErrorActionPreference = 'Stop'
$informe = $PSScriptRoot
$out = Join-Path $informe 'build'
New-Item -ItemType Directory -Force $out | Out-Null

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    throw 'No se encuentra pandoc. Instalalo desde https://pandoc.org/installing.html'
}

$secciones = Get-ChildItem (Join-Path $informe 'secciones') -Filter '*.md' | Sort-Object Name | ForEach-Object { $_.FullName }
$comunes = @(
    '--from', 'markdown',
    '--toc',
    '--metadata-file', (Join-Path $informe 'metadata.yaml'),
    '--resource-path', $informe
)

$engine = @('xelatex', 'lualatex', 'pdflatex') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1

# pandoc y LaTeX escriben avisos por stderr (por ejemplo, glifos que faltan en
# la fuente). Con ErrorActionPreference=Stop eso abortaria la compilacion, asi
# que se desactiva solo durante la llamada y se comprueba el codigo de salida.
$anterior = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    if ($engine) {
        $destino = Join-Path $out 'Memoria_Grupo_CBI.pdf'
        & pandoc @secciones @comunes "--pdf-engine=$engine" '-o' $destino
    } else {
        $destino = Join-Path $out 'Memoria_Grupo_CBI.docx'
        Write-Warning 'No hay motor LaTeX (xelatex/lualatex/pdflatex): se genera .docx. Exportalo a PDF desde Word.'
        & pandoc @secciones @comunes '-o' $destino
    }
    $codigo = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $anterior
}

if ($codigo -ne 0) { throw "pandoc termino con codigo $codigo" }
Write-Host "Memoria generada: $destino"
