{
  pkgs,
  inputs,
  ...
}: {
  # https://devenv.sh/basics/

  # https://devenv.sh/packages/
  packages = with pkgs; [
    git

    # quarto pinned to 1.6.43 (see devenv.yaml nixpkgs-quarto input):
    # the dfolio/quarto-ieee extension is built/tested against ~1.5/1.6;
    # the pin keeps the format module and deno runtime mutually consistent
    inputs.nixpkgs-quarto.legacyPackages.${pkgs.system}.quarto

    # TeX Live for the IEEE journal template: quarto only whitelists
    # pdflatex/xelatex/lualatex/latexmk as PDF engines (no tectonic), and
    # the custom-template format requires a recognized LaTeX engine
    (texlive.withPackages (ps:
      with ps; [
        scheme-small # base LaTeX toolchain (pdflatex, latexmk...)
        collection-publishers # IEEEtran.cls
        collection-latexextra # physics, float, orcidlink
        collection-mathscience # mhchem
        collection-bibtexextra # IEEEtran.bst
      ]))
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    venv.requirements = ./requirements.txt;
    libraries = [pkgs.zlib]; # native libs needed by pip wheels (numpy/pandas links against libz.so.1)
  };

  # https://devenv.sh/scripts/
  scripts.render-report.exec = ''
    # report.qmd -> output/ (PDF IEEE via pdflatex; quarto 1.6.43 travado).
    # QUARTO_PYTHON fixado no interpretador do venv do projeto — o quarto usa
    # esse kernel para executar os chunks; o venv tem nbclient/nbformat
    # porque o kernel runner precisa deles.
    export QUARTO_PYTHON="$(command -v python)"
    mkdir -p output
    quarto render report.qmd --output-dir output
  '';
}
