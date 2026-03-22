{
  lib,
  python3Packages,
  self,
  ...
}:
let
  disnake = python3Packages.disnake.overrideAttrs (old: {
    src = self.pins.disnake;

    propagatedBuildInputs =
      with python3Packages;
      old.propagatedBuildInputs
      ++ [
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

  src = lib.cleanSource ./.;

  pyproject = true;
  build-system = [ python3Packages.setuptools ];

  propagatedBuildInputs = with python3Packages; [
    aiohttp
    audioop-lts
    disnake
    disnake_paginator
    psutil
    typing-extensions
    youtube-transcript-api
    yt-dlp
  ];

  doCheck = false;
}
