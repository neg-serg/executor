{
  description = "Simple terminal manager";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication mkPoetryPackages defaultPoetryOverrides;
        pypkgs-build-requirements = {
            python-xlib = ["setuptools" "scikit-build"];
            ruamel-std-argparse= [ "setuptools" ];
        };
        p2n-overrides = defaultPoetryOverrides.extend (self: super:
          builtins.mapAttrs (package: build-requirements:
            (builtins.getAttr package super).overridePythonAttrs (old: {
              # nativeBuildInputs = [ pkgs.cmake ] ++ old.nativeBuildInputs;
              buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg:
                if builtins.isString pkg then
                  builtins.getAttr pkg super
                else
                  pkg) build-requirements);
            })) pypkgs-build-requirements);
      in {
        packages = {
          executor = mkPoetryApplication {
              projectDir = self;
              overrides = p2n-overrides;
          };
          default = self.packages.${system}.executor;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.executor ];
          packages = [ pkgs.poetry ];
        };
      });
}
