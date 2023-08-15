#include "pico/stdlib.h"

#include <stdio.h>

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include "ImageData.h"
#include <stdlib.h> // malloc() free()
#include <string.h>
#include <stdio.h>

#include "LCD_2in.h"
#include "LCDScript.c"
int main() {

    DEV_Delay_ms(100);
    printf("LCD_2in_test Demo\r\n");
    if(DEV_Module_Init()!=0){
        return -1;
    }
    DEV_SET_PWM(50);
    /* LCD Init */
    printf("2inch LCD demo...\r\n");
    LCD_2IN_Init(HORIZONTAL);
    LCD_2IN_Clear(WHITE);
    
    //LCD_SetBacklight(1023);
    UDOUBLE Imagesize = LCD_2IN_HEIGHT*LCD_2IN_WIDTH*2;
    UWORD *BlackImage;
    if((BlackImage = (UWORD *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }
    // /*1.Create a new image cache named IMAGE_RGB and fill it with white*/
    Paint_NewImage((UBYTE *)BlackImage,LCD_2IN.WIDTH,LCD_2IN.HEIGHT, 90, WHITE);
    Paint_SetScale(65);
    Paint_Clear(RAISIN);
    Paint_SetRotate(ROTATE_270);

    opening_screen(BlackImage);
    Paint_Clear(RAISIN);
    while(1){

        printf("PING\n");
        // int pingchar[15];
        // snprintf(pingchar, 15, "Drawing: %d", counter);
   	    // Paint_DrawString_EN(8, counter, pingchar, &Font20, WHITE, RAISIN);
        main_menu(BlackImage);
        DEV_Delay_ms(1000);
		LCD_2IN_Display((uint8_t * )BlackImage);             
    }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    
    DEV_Module_Exit();
    return 0;

}

