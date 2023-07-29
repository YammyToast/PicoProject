#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include "ImageData.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

int LCD_2in_test(void)
{

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
    Paint_Clear(WHITE);
    Paint_SetRotate(ROTATE_270);
    // /* GUI */
    printf("drawing...\r\n");
    // /*2.Drawing on the image*/
    
#if 1
    Paint_DrawPoint(2,1, BLACK, DOT_PIXEL_1X1,  DOT_FILL_RIGHTUP);//240 240
    Paint_DrawPoint(2,6, BLACK, DOT_PIXEL_2X2,  DOT_FILL_RIGHTUP);
    Paint_DrawPoint(2,11, BLACK, DOT_PIXEL_3X3, DOT_FILL_RIGHTUP);
    Paint_DrawPoint(2,16, BLACK, DOT_PIXEL_4X4, DOT_FILL_RIGHTUP);
    Paint_DrawPoint(2,21, BLACK, DOT_PIXEL_5X5, DOT_FILL_RIGHTUP);
    Paint_DrawLine( 10,  5, 40, 35, MAGENTA, DOT_PIXEL_2X2, LINE_STYLE_SOLID);
    Paint_DrawLine( 10, 35, 40,  5, MAGENTA, DOT_PIXEL_2X2, LINE_STYLE_SOLID);

    Paint_DrawLine( 80,  20, 110, 20, CYAN, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);
    Paint_DrawLine( 95,   5,  95, 35, CYAN, DOT_PIXEL_1X1, LINE_STYLE_DOTTED);

    Paint_DrawRectangle(10, 5, 40, 35, RED, DOT_PIXEL_2X2,DRAW_FILL_EMPTY);
    Paint_DrawRectangle(45, 5, 75, 35, BLUE, DOT_PIXEL_2X2,DRAW_FILL_FULL);

    Paint_DrawCircle(95, 20, 15, GREEN, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    Paint_DrawCircle(130, 20, 15, GREEN, DOT_PIXEL_1X1, DRAW_FILL_FULL);


    Paint_DrawNum (50, 40 ,9.87654321, &Font20,5,  WHITE,  BLACK);
    Paint_DrawString_EN(1, 40, "Swag", &Font20, 0x000f, 0xfff0);
    Paint_DrawString_CN(1,60, "Messiah",  &Font24CN, WHITE, BLUE);
    Paint_DrawString_EN(1, 100, "Yames", &Font16, RED, WHITE); 

    // /*3.Refresh the picture in RAM to LCD*/
    LCD_2IN_Display((UBYTE *)BlackImage);
    DEV_Delay_ms(1000);

#endif
#if 1
     Paint_DrawImage1(gImage_2inch_1,0,0,320,240);
     LCD_2IN_Display((UBYTE *)BlackImage);
     DEV_Delay_ms(2000);
     
#endif
	// 4.Test button
   int key0 = 15; 
   int key1 = 17; 
   int key2 = 2; 
   int key3 = 3; 
   
   SET_Infrared_PIN(key0);    
   SET_Infrared_PIN(key1);
   SET_Infrared_PIN(key2);
   SET_Infrared_PIN(key3);

   Paint_Clear(WHITE);
   LCD_2IN_Display((uint8_t * )BlackImage);
   
   while(1){
   	Paint_DrawString_EN(70, 100, "Extra Swag", &Font20, WHITE, RED);
       if(DEV_Digital_Read(key0 ) == 0){
       
       	Paint_DrawRectangle(288, 208, 308, 228, YELLOW, DOT_PIXEL_1X1,DRAW_FILL_FULL);
		
       }else  {
       	Paint_DrawRectangle(288, 208, 308, 228, RED, DOT_PIXEL_1X1,DRAW_FILL_FULL);
       }
           
       if(DEV_Digital_Read(key1 ) == 0){
       
          Paint_DrawRectangle(12, 208, 32, 228, YELLOW, DOT_PIXEL_1X1,DRAW_FILL_FULL);
			
       }else  {
           
        	Paint_DrawRectangle(12, 208, 32, 228, RED, DOT_PIXEL_1X1,DRAW_FILL_FULL);
       }
       
       if(DEV_Digital_Read(key2) == 0){
       
           
			Paint_DrawRectangle(12, 12, 32, 32, YELLOW, DOT_PIXEL_1X1,DRAW_FILL_FULL);
       }else  {
           
       	Paint_DrawRectangle(12, 12, 32, 32, RED, DOT_PIXEL_1X1,DRAW_FILL_FULL);
       }
       
       if(DEV_Digital_Read(key3 ) == 0){
       
           
            Paint_DrawRectangle(288, 12, 308, 32, YELLOW, DOT_PIXEL_1X1,DRAW_FILL_FULL);

       }else{
           
            Paint_DrawRectangle(288, 12, 308, 32, RED, DOT_PIXEL_1X1,DRAW_FILL_FULL);   
      
       }		
		LCD_2IN_Display((uint8_t * )BlackImage);             
   }

    /* Module Exit */
    free(BlackImage);
    BlackImage = NULL;
    
    
    DEV_Module_Exit();
    return 0;
}


int main() {
    const uint led_pin = 25;

    gpio_init(led_pin);
    gpio_set_dir(led_pin, GPIO_OUT);

    for(int i = 0; i < 5; i++) {
        gpio_put(led_pin, true);
        sleep_ms(1000);
        gpio_put(led_pin, false);
        sleep_ms(1000);
    }

    LCD_2in_test();
}

