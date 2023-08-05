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

    enum window_state state = 0;
    enum window_state last_state = state;

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
   
    Paint_Clear(RAISIN);
    // opening_screen();
    // DEV_Delay_ms(1000);
    // Paint_Clear(RAISIN);

    int (*render_func_ptr)(void) = &opening_screen;
    int (*last_func_ptr)(void);

    while(1){

        if (last_state != state) {
            Paint_Clear(RAISIN);
            last_state = state;
        }

        gpio_put(led_pin, true);
        sleep_ms(1000);
        gpio_put(led_pin, false);
        sleep_ms(1000);

        state = (*render_func_ptr)();

        switch (state) {
            case 0:
                (render_func_ptr) = &opening_screen;
            case 1:
                (render_func_ptr) = &main_menu;
            default:
                (render_func_ptr) = &main_menu;

        }

         
    }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    
    DEV_Module_Exit();
    return 0;

}

