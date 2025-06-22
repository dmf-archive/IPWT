$markdownFile = "src/manuscript_en.md"
$bibFile = "src/references.bib"
$tempTexFile = "src-tex/manuscript_en.tex"

pandoc $markdownFile --bibliography=$bibFile --citeproc -s -o $tempTexFile -V classoption:a4paper -V hyperrefoptions:breaklinks=true
