## Build

! - Run install.sh to install linker dependencies.

1 - Run configure.sh to assemble linker.
    ```
    bash ./configure.sh
    ```

2 - Create build directory if it doesn't already exist.
    ```
    mkdir build
    cd build
    ```

3 - Run CMake in the build directory.
    ```
        cmake ../
    ```

4 - Run make in the build directory.
    ```
        make
    ```

5 - Upload generated UF2 file to Raspberry Pi Pico