#include "config.h"

#include "linker.h"
#include "linker.c"

#ifndef CORE_CONFIG_MAIN
#define CORE_CONFIG_MAIN

    // widget_link* widget_links;
    
    // UDOUBLE image_size;
    // UWORD* black_image;

    // int padding;

    // float dialogue_split_ratio;
    // float carousel_split_ratio;

    // int widget_frame_height;
    // int widget_frame_width;

    // int dialogue_frame_height;
    // int dialogue_frame_width;

system_variables get_system_variables(UWORD* _black_image, UDOUBLE _image_size) {

    int padding = 8;
    float dialogue_split_ratio = 0.375;
    float carousel_split_ratio = 0.1;

    int calculated_frame_height = LCD_2IN_HEIGHT - (2 * padding);
    int calculated_frame_width = LCD_2IN_WIDTH - (2 * padding);
    

    system_variables vars = {
        .widget_links = widget_links,
        .image_size = _image_size,
        .black_image = _black_image,
        .padding = padding,
        .dialogue_split_ratio = dialogue_split_ratio,
        .carousel_split_ratio = carousel_split_ratio,
        .widget_frame_width = calculated_frame_width,
        .widget_frame_height = (int)(calculated_frame_height * (1 - dialogue_split_ratio)),
        .dialogue_frame_width = calculated_frame_width,
        .dialogue_frame_height = (int)(calculated_frame_height * dialogue_split_ratio)
    };
    return vars;
}

void destruct_system_variables(system_variables sys_vars) {
    printf("TODO!");
}



#endif