#include "linker.h"
#include "linker.c"


#include "LCD_2in.h"
#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"

#ifndef CORE_CONFIG_H
#define CORE_CONFIG_H

struct image_link {


};

typedef struct 
{
    const widget_link* widget_links;
    
    UDOUBLE image_size;
    UWORD* black_image;

    int padding;

    float dialogue_split_ratio;
    float carousel_split_ratio;

    int widget_frame_height;
    int widget_frame_width;

    int dialogue_frame_height;
    int dialogue_frame_width;

} system_variables;  

system_variables get_system_variables(UWORD*, UDOUBLE);
void destruct_system_variables(system_variables sys_vars);

#endif