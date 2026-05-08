{
  cmake,
  lib,
  ninja,
  nlohmann_json,
  openssl,
  python3Packages,
  self,
  stdenv,
}:
let
  mlspp = stdenv.mkDerivation {
    pname = "mlspp";
    version = self.pins.mlspp.revision;

    src = self.pins.mlspp;

    nativeBuildInputs = [
      cmake
      ninja
    ];

    buildInputs = [
      openssl
      nlohmann_json
    ];

    postPatch = ''
      substituteInPlace CMakeLists.txt \
        --replace-fail "-Wextra -Werror -Wmissing-declarations" "-Wextra -Wmissing-declarations"
    '';

    cmakeFlags = [
      "-DDISABLE_GREASE=ON"
      "-DMLS_CXX_NAMESPACE=mlspp"
      "-DBUILD_TESTING=OFF"
    ];

    meta = {
      description = "Cisco MLS C++ library";
      homepage = "https://github.com/cisco/mlspp";
      license = lib.licenses.bsd2;
      platforms = lib.platforms.unix;
    };
  };
in
python3Packages.buildPythonPackage {
  pname = "dave.py";
  version = self.pins."dave.py".revision;
  pyproject = true;

  src = self.pins."dave.py";

  build-system = with python3Packages; [
    nanobind
    scikit-build-core
  ];

  postPatch = ''
        substituteInPlace pyproject.toml \
          --replace-fail "nanobind~=2.10.2" "nanobind>=2.10.2"

        substituteInPlace CMakeLists.txt \
          --replace-fail \
            'set(VCPKG_MANIFEST_DIR "''${LIBDAVE_SRC_PATH}/vcpkg-alts/''${LIBDAVE_CRYPTO}" CACHE STRING "")' \
            'set(VCPKG_MANIFEST_DIR "''${LIBDAVE_SRC_PATH}/vcpkg-alts/''${LIBDAVE_CRYPTO}" CACHE STRING "")
    option(DAVE_USE_SYSTEM_DEPS "Use system CMake packages instead of the bundled vcpkg toolchain" OFF)' \
          --replace-fail \
            'set(_VCPKG_TOOLCHAIN "''${LIBDAVE_SRC_PATH}/vcpkg/scripts/buildsystems/vcpkg.cmake")' \
            'if (NOT DAVE_USE_SYSTEM_DEPS)
    set(_VCPKG_TOOLCHAIN "''${LIBDAVE_SRC_PATH}/vcpkg/scripts/buildsystems/vcpkg.cmake")' \
          --replace-fail \
            'message(STATUS "Using vcpkg toolchain ''${CMAKE_TOOLCHAIN_FILE}")' \
            'message(STATUS "Using vcpkg toolchain ''${CMAKE_TOOLCHAIN_FILE}")
    else()
        message(STATUS "Using system dependencies")
    endif()'

        substituteInPlace scripts/collect_licenses.py \
          --replace-fail \
            'parser.add_argument("vcpkg_installed_dir", type=Path)' \
            'parser.add_argument("--skip-vcpkg-deps", action="store_true")
    parser.add_argument("vcpkg_installed_dir", type=Path)' \
          --replace-fail \
            'vcpkg_deps = [
        "mlspp",
        "nlohmann-json",
        "boringssl" if args.crypto == "boringssl" else "openssl",
    ]
    LICENSE_PATHS.update(
        {dep: (args.vcpkg_installed_dir / "share" / dep / "copyright") for dep in vcpkg_deps}
    )' \
            'if not args.skip_vcpkg_deps:
        vcpkg_deps = [
            "mlspp",
            "nlohmann-json",
            "boringssl" if args.crypto == "boringssl" else "openssl",
        ]
        LICENSE_PATHS.update(
            {dep: (args.vcpkg_installed_dir / "share" / dep / "copyright") for dep in vcpkg_deps}
        )'

        substituteInPlace CMakeLists.txt \
          --replace-fail \
            'COMMAND "''${Python_EXECUTABLE}" "scripts/collect_licenses.py"' \
            'COMMAND "''${Python_EXECUTABLE}" "scripts/collect_licenses.py" --skip-vcpkg-deps'
  '';

  nativeBuildInputs = [
    cmake
    ninja
  ];

  dontUseCmakeConfigure = true;

  buildInputs = [
    openssl
    nlohmann_json
    mlspp
  ];

  dependencies = [ ];

  nativeCheckInputs = with python3Packages; [
    pytestCheckHook
  ];

  SKBUILD_CMAKE_ARGS = "-DDAVE_USE_SYSTEM_DEPS=ON";

  pythonImportsCheck = [ "dave" ];

  meta = {
    description = "Python bindings for libdave, Discord's audio & video end-to-end encryption";
    homepage = "https://github.com/DisnakeDev/dave.py";
    changelog = "https://github.com/DisnakeDev/dave.py/blob/main/docs/CHANGELOG.md";
    license = lib.licenses.mit;
  };
}
