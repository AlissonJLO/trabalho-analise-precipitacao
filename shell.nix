{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.virtualenv
    pkgs.zlib
    pkgs.stdenv.cc.cc.lib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH
    export VENV=.venv
    if [ ! -d $VENV ]; then
      python -m venv $VENV
    fi
    source $VENV/bin/activate

    export PYTHONPATH=$PWD:$PYTHONPATH
    echo "Ambiente Nix ativado com sucesso."
  '';
}
