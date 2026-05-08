{
  callPackage,
  ffmpeg,
  lib,
  libopus,
  python3Packages,
  self,
}:
let
  dave_py = callPackage ./dave_py.nix { inherit self; };

  disnake = python3Packages.disnake.overrideAttrs (old: {
    src = self.pins.disnake;

    propagatedBuildInputs =
      with python3Packages;
      old.propagatedBuildInputs
      ++ [
        dave_py
        typing-extensions
        versioningit
      ];

    nativeBuildInputs = old.nativeBuildInputs ++ [ python3Packages.hatchling ];
  });

  disnake_paginator = python3Packages.buildPythonPackage {
    pname = "disnake-paginator";
    version = "1.0.8";

    src = self.pins.disnake-paginator;

    pyproject = true;
    build-system = [ python3Packages.setuptools ];

    propagatedBuildInputs = [
      disnake
    ];

    doCheck = false;
  };
in
python3Packages.buildPythonApplication {
  pname = "errornocord";
  version = "0.1.0";

  src = lib.cleanSource ../.;

  pyproject = true;
  build-system = [ python3Packages.setuptools ];

  propagatedBuildInputs = with python3Packages; [
    aiohttp
    audioop-lts
    psutil
    typing-extensions
    youtube-transcript-api
    yt-dlp

    disnake
    disnake_paginator

    ffmpeg
    libopus
  ];

  doCheck = false;

  meta = {
    description = "Hot-reloadable Discord music bot";
    homepage = "https://github.com/ErrorNoInternet/ErrorNoCord";
    license = lib.licenses.gpl3Only;
    mainProgram = "errornocord";
  };
}
