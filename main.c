#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()
#include <string.h>
#include <stdio.h>

#include "LCD_2in.h"
#include "LCDScript.c"

#include "linker.h"
#include "linker.c"

#include "config.h"
#include "config.c"

const float split_ratio = 0.375;
system_variables sys_vars;

int main() {
    // LCD_SetBacklight(1023);
    UDOUBLE image_size = LCD_2IN_HEIGHT*LCD_2IN_WIDTH*2;
    UWORD *black_image;
    if((black_image = (UWORD *)malloc(image_size)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }

    sys_vars = get_system_variables(black_image, image_size);
    // printf("var: %d\n", sys_vars.widget_frame_height);

    initialize_settings(sys_vars.black_image, sys_vars.image_size );
    // initialize_settings(sys_vars.image_size, sys_vars.black_image);
    



    // opening_screen(sys_vars.black_image);
    opening_screen(sys_vars.black_image);

    Paint_Clear(RAISIN);

    int padding = 8;
    int calculated_frame_height = LCD_2IN_HEIGHT - (2 * padding);
    int calculated_frame_width = LCD_2IN_WIDTH - (2 * padding);
    
    // int image_frame_height = (int)(calculated_frame_height * split_ratio);
    // int widget_frame_height = (int)(calculated_frame_height * (1 - split_ratio));
    
    while(1){

        // main_menu(BlackImage);
        // render_frame(padding, calculated_frame_width, calculated_frame_height, &split_ratio, RAISIN, WHITE);

        // DEV_Delay_ms(1000);

		// LCD_2IN_Display((uint8_t * )BlackImage);             
    }

    /* Module Exit */
    free(sys_vars.black_image);
    sys_vars.black_image = NULL;
    
    // free(widget_func_ptrs);
    DEV_Module_Exit();
    return 0;

}

