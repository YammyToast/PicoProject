cmake_minimum_required(VERSION 3.12)

include(/home/yammy/Code/pico-sdk/external/pico_sdk_import.cmake)
#include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
#include(../../pico-sdk/external/pico_sdk_import.cmake)

project(pico_main VERSION 0.1 LANGUAGES C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(${PROJECT_NAME}
main.c
)
configure_file(${PROJECT_SOURCE_DIR}/include/ProjectConfig.h.in ${PROJECT_SOURCE_DIR}/include/ProjectConfig.h)
target_include_directories(${PROJECT_NAME} PUBLIC "${PROJECT_BINARY_DIR}")

add_subdirectory(lib/Config)
add_subdirectory(lib/Infrared)
add_subdirectory(lib/LCD)
add_subdirectory(lib/Fonts)
add_subdirectory(lib/GUI)


include_directories(
        ${PROJECT_SOURCE_DIR}/include
        ${PROJECT_SOURCE_DIR}/src
        )



file(GLOB all_SRCS
        "${PROJECT_SOURCE_DIR}/include/*.h"
        "${PROJECT_SOURCE_DIR}/include/*.hpp"
        "${PROJECT_SOURCE_DIR}/src/*.cpp"
        "${PROJECT_SOURCE_DIR}/src/*.c"
)


include_directories(./lib/Config)
include_directories(./lib/GUI)
include_directories(./lib/LCD)
include_directories(./lib/Infrared)


pico_add_extra_outputs(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME}
    pico_stdlib
    LCD
    Infrared 
    GUI 
    Fonts 
    Config 
    hardware_spi
)

pico_enable_stdio_usb(${PROJECT_NAME} 0)
pico_enable_stdio_uart(${PROJECT_NAME} 1)