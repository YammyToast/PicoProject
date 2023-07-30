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

int main() {
    const uint led_pin = 25;
    const uint button1_pin = 20;

    gpio_init(led_pin);
    gpio_set_dir(led_pin, GPIO_OUT);
    
    gpio_set_dir(button1_pin, GPIO_IN);

    UDOUBLE Imagesize = LCD_2IN_HEIGHT*LCD_2IN_WIDTH*2;
    UWORD *BlackImage;

    if(initialize_settings(Imagesize, BlackImage)!=0) {
        printf("Failed to initialize settings... \r\n");
        exit(0);
    }

    if((BlackImage = (UWORD *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        return -1;
    }
    // /*1.Create a new image cache named IMAGE_RGB and fill it with white*/
    Paint_NewImage((UBYTE *)BlackImage,LCD_2IN.WIDTH,LCD_2IN.HEIGHT, 90, WHITE);

    // Don't change this value or else everything fucking dies
    Paint_SetScale(65);

    Paint_SetRotate(ROTATE_270);
    // /* GUI */


    LCD_2IN_Display((uint8_t * )BlackImage);
   
    Paint_Clear(RED);
    opening_screen();
    Paint_Clear(RAISIN);


    while(1){

        gpio_put(led_pin, true);
        sleep_ms(1000);
        gpio_put(led_pin, false);
        sleep_ms(1000);


        // Paint_DrawImage1(gImage_2inch_1,0,0,320,240);
        LCD_2IN_Display((UBYTE *)BlackImage);
        DEV_Delay_ms(10);
        
   	    Paint_DrawString_EN(8, 8, "Main Menu", &Font24, WHITE, RAISIN);
       		
		LCD_2IN_Display((uint8_t * )BlackImage);             
    }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    
    DEV_Module_Exit();
    return 0;

}

