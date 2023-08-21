#include "pico/stdlib.h"


#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include "ImageData.h"
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
    printf("MAX: %d\n", widget_count);
    int rotate = 0;

    while(1){
        if(rotate > (widget_count - 1)) {
            rotate = 0;
        }
        // printf("PING %d\n", rotate);
        DEV_Delay_ms(1000);
        (widget_links[rotate].display)(BlackImage);
        DEV_Delay_ms(1000);
        Paint_Clear(RAISIN);
        rotate = rotate + 1;
        
        printf("RATIO: %.6f\n", split_ratio);

        // int pingchar[15];
        // snprintf(pingchar, 15, "Drawing: %d", counter);
   	    // Paint_DrawString_EN(8, counter, pingchar, &Font20, WHITE, RAISIN);
        // main_menu(BlackImage);


		// LCD_2IN_Display((uint8_t * )BlackImage);             
    }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    // free(widget_func_ptrs);
    DEV_Module_Exit();
    return 0;

}

