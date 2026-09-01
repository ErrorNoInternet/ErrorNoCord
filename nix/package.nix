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

  disnake = python3Packages.disnake.overrideAttrs (
    old:
    let
      version = lib.strings.removePrefix "v" self.pins.disnake.version;
      versionParts = lib.splitVersion version;
    in
    {
      src = self.pins.disnake;
      inherit version;

      propagatedBuildInputs =
        with python3Packages;
        old.propagatedBuildInputs
        ++ [
          dave_py
          typing-extensions
          versioningit
        ];

      nativeBuildInputs = old.nativeBuildInputs ++ [
        python3Packages.hatchling
        python3Packages.pyprojectVersionPatchHook
      ];

      postPatch = (old.postPatch or "") + ''
        cat > disnake/_version.py <<EOF
        # SPDX-License-Identifier: MIT

        from typing import Literal, NamedTuple

        __version__ = "${version}"


        class VersionInfo(NamedTuple):
            major: int
            minor: int
            micro: int
            releaselevel: Literal["alpha", "beta", "candidate", "final"]
            serial: int

        version_info: VersionInfo = VersionInfo(${builtins.elemAt versionParts 0}, ${builtins.elemAt versionParts 1}, ${builtins.elemAt versionParts 2}, "final", 0)
        EOF
      '';

      doCheck = false;
      dontUsePytestCheck = true;
    }
  );

  disnake_paginator = python3Packages.buildPythonPackage {
    pname = "disnake-paginator";
    version = "1.0.8";
    pyproject = true;

    src = self.pins.disnake-paginator;

    build-system = [ python3Packages.setuptools ];

    propagatedBuildInputs = [
      disnake
    ];

    doCheck = false;
  };
in
python3Packages.buildPythonApplication {
  pname = "errornocord";
  version = self.rev or self.dirtyRev or "0.1.0";
  pyproject = true;

  src = lib.cleanSource ../.;

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
