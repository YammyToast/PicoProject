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

const float split_ratio = 0.375;

int main() {
    //LCD_SetBacklight(1023);
    UDOUBLE Imagesize = LCD_2IN_HEIGHT*LCD_2IN_WIDTH*2;
    UWORD *BlackImage;
    if((BlackImage = (UWORD *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }

    initialize_settings(Imagesize, BlackImage);
    
    // (widget_links[0].display)(BlackImage);
    // DEV_Delay_ms(2000);
    // Paint_Clear(RAISIN);
    // DEV_Delay_ms(2000);
    // (widget_links[1].display)(BlackImage);
    // DEV_Delay_ms(2000);
    // Paint_Clear(RAISIN);
    // DEV_Delay_ms(2000);

    opening_screen(BlackImage);

    Paint_Clear(RAISIN);

    int padding = 8;
    int calculated_frame_height = LCD_2IN_HEIGHT - (2 * padding);
    int calculated_frame_width = LCD_2IN_WIDTH - (2 * padding);
    
    // int image_frame_height = (int)(calculated_frame_height * split_ratio);
    // int widget_frame_height = (int)(calculated_frame_height * (1 - split_ratio));
    
    while(1){

        // main_menu(BlackImage);
        render_frame(padding, calculated_frame_width, calculated_frame_height, &split_ratio, RAISIN, WHITE);

        DEV_Delay_ms(1000);

		LCD_2IN_Display((uint8_t * )BlackImage);             
    }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    // free(widget_func_ptrs);
    DEV_Module_Exit();
    return 0;

}

