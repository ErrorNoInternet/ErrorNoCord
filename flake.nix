{
  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";

    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { flake-parts, self, ... }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "aarch64-linux"
        "x86_64-linux"
      ];

      perSystem =
        { pkgs, self', ... }:
        {
          devShells.default = pkgs.mkShell {
            name = "errornocord";
            inputsFrom = [ self'.packages.default ];
            buildInputs = [ self'.packages.default ];
          };

          packages = rec {
            default = errornocord;
            errornocord = pkgs.callPackage ./nix/package.nix { inherit self; };
          };
        };

      flake.pins = import ./nix/npins;
    };

  description = "Hot-reloadable Discord music bot";
}
