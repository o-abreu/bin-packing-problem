{
  config,
  pkgs,
  inputs,
  ...
}: let
  quartoPinned = inputs.nixpkgs-quarto.legacyPackages.${pkgs.system}.quarto;
  venvPython = "${config.devenv.root}/.devenv/state/venv/bin/python";
  quarto = pkgs.runCommand "quarto-${quartoPinned.version}-venv" {} ''
    mkdir -p $out/bin
    install -m755 ${quartoPinned}/bin/quarto $out/bin/quarto

    # remove o bloco "--prefix QUARTO_PYTHON" gerado pelo makeWrapper
    sed -i '/^QUARTO_PYTHON=/,/^export QUARTO_PYTHON$/d' $out/bin/quarto
    # e fixa o interpretador do venv no lugar
    sed -i "s|^exec -a|export QUARTO_PYTHON='${venvPython}'\nexec -a|" $out/bin/quarto

    # falha ruidosamente se o layout do wrapper mudar (bump do nixpkgs-quarto)
    grep -qF "export QUARTO_PYTHON='${venvPython}'" $out/bin/quarto \
      || { echo "quarto: patch do wrapper falhou (layout do nixpkgs mudou?)" >&2; exit 1; }
  '';
in {
  env = {
    GRB_LICENSE_FILE = "${config.devenv.root}/gurobi.lic";
  };

  packages = with pkgs; [
    git
    gurobi
    quarto
    (texlive.withPackages (ps:
      with ps; [
        scheme-small # base LaTeX toolchain (pdflatex, latexmk...)
        collection-publishers # IEEEtran.cls
        collection-latexextra # physics, float, orcidlink
        collection-mathscience # mhchem
        collection-bibtexextra # IEEEtran.bst
      ]))
  ];

  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    venv.requirements = ./requirements.txt;
    libraries = [
      pkgs.zlib # numpy/pandas wheels link against libz.so.1
      pkgs.stdenv.cc.cc.lib # libstdc++/libgcc_s, exigidos pela libgurobi do wheel
    ];
  };

  # report/main.qmd -> output/ (PDF IEEE via pdflatex; quarto 1.6.43 travado).
  scripts.render-report.exec =
    # bash
    ''
      mkdir -p output
      quarto render report/main.qmd --output-dir output
    '';
}
