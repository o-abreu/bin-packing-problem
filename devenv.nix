{
  config,
  pkgs,
  inputs,
  ...
}: let
  quartoPinned = inputs.nixpkgs-quarto.legacyPackages.${pkgs.system}.quarto;
  # flake do presenterm: packages.<system>.default (o Cargo.toml do master
  # ainda reporta "0.16.1"; a featureset é pós-alinhamento)
  presenterm = inputs.presenterm.packages.${pkgs.system}.default;
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
    presenterm
    quarto
    python3Packages.weasyprint # exportação do presenterm (-e) para validar a estrutura do deck
    pandoc # blocos ```latex +render``` do deck (LaTeX → código typst)
    typst # motor final da renderização LaTeX do presenterm (typst → imagem)
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

  scripts = {
    presenter.exec =
      # bash
      ''
        set -o errexit
        set -o nounset
        set -o pipefail

        # presenterm do flake do projeto; wezterm, jq e hyprctl vêm do PATH
        # herdado (o wrapper roda dentro do devenv shell).
        export PATH="${presenterm}/bin:$PATH"

        # INFO: Lança o presenterm numa janela WezTerm dedicada, em tela cheia.
        #
        # presenterm é uma TUI: rodado diretamente, herda o terminal corrente
        # (tamanho de fonte, barra, geometria). Isso serve para folhear o deck,
        # não para apresentar de pé. Então: abre um WezTerm descartável do
        # tamanho da sala, o marca com um --class conhecido para o compositor
        # encontrá-lo, e o põe em tela cheia.
        #
        # Uso: presenter [-s|--font-size TAM] [-l|--line-height LH]
        #      [opções do presenterm...] <arquivo-markdown>
        #
        # --font-size e --line-height são consumidos aqui; todo o resto é
        # repassado verbatim ao presenterm. O ÚLTIMO argumento é o arquivo do
        # deck, resolvido com realpath para sobreviver ao lançamento da janela.

        font_size=12
        # INFO: o line_height padrão do WezTerm (1,0) aperta as linhas. Numa
        # projeção, a leading extra lê melhor; padrão 1,3.
        line_height=1.3
        presenterm_args=()

        while [[ $# -gt 0 ]]; do
          case "$1" in
          -s | --font-size)
            font_size="$2"
            shift 2
            ;;
          -l | --line-height)
            line_height="$2"
            shift 2
            ;;
          *)
            presenterm_args+=("$1")
            shift
            ;;
          esac
        done

        if [[ ''${#presenterm_args[@]} -eq 0 ]]; then
          echo "Usage: $0 [--font-size SIZE] [--line-height LH] [presenterm-options...] <markdown-file>" >&2
          exit 1
        fi

        last_idx=$((''${#presenterm_args[@]} - 1))
        markdown_file="''${presenterm_args[$last_idx]}"

        if [[ ! -f "$markdown_file" ]]; then
          echo "Error: File '$markdown_file' not found" >&2
          echo "Usage: $0 [--font-size SIZE] [--line-height LH] [presenterm-options...] <markdown-file>" >&2
          exit 1
        fi

        markdown_file=$(realpath "$markdown_file")
        presenterm_args[$last_idx]="$markdown_file"

        # shellcheck disable=SC2016
        # INFO: o `sleep 0.5` dá tempo de a janela assentar (e aplicar os
        # --config) antes de o presenterm desenhar; sem ele a TUI pode
        # renderizar na geometria antiga. Em falha, a janela fica aberta para o
        # erro poder ser lido. `--cwd` preserva o diretório de chamada, que o
        # presenterm precisa para resolver caminhos relativos de imagens.
        wezterm \
          --config "enable_tab_bar=false" \
          --config "font_size=''${font_size}" \
          --config "line_height=''${line_height}" \
          start \
          --class "presenterm" \
          --cwd "$(pwd)" \
          -- bash -c 'sleep 0.5; presenterm "$@"; rc=$?; if [ $rc -ne 0 ]; then echo "presenterm failed with exit code $rc"; read -n1 -p "Press any key to close..."; fi; exit $rc' _ "''${presenterm_args[@]}" &

        wezterm_pid=$!

        # INFO: o WezTerm não dá handle na nova janela, então consulta o
        # Hyprland pela janela com o --class marcado, foca e maximiza.
        # Limitado a ~2 s; se nunca aparecer, apenas salta o foco em vez de
        # travar.
        for _ in $(seq 1 20); do
          addr=$(hyprctl clients -j | jq -r '[.[] | select(.class == "presenterm") | .address][0] // empty')
          if [[ -n "$addr" && "$addr" != "null" ]]; then
            hyprctl dispatch focuswindow "address:''${addr}"
            hyprctl dispatch fullscreen 1
            break
          fi
          sleep 0.1
        done

        # INFO: bloqueia até a janela fechar, para o `presenter` se comportar
        # como comando em primeiro plano (o prompt só volta depois da palestra).
        wait "$wezterm_pid" 2>/dev/null || true
      '';

    # report/main.qmd -> report/main.pdf (PDF IEEE via pdflatex; quarto 1.6.43
    # travado). Sem `--output-dir`: o Quarto resolve esse caminho em relação ao
    # arquivo de entrada, e o destino tem de ser o mesmo do `quarto preview` do
    # Neovim (o PDF ao lado da fonte) para existir uma única cópia do relatório.
    render-report.exec =
      # bash
      ''
        cd "${config.devenv.root}"
        quarto render report/main.qmd
      '';
  };
}
