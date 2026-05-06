#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include "DHT.h"
#include <LiquidCrystal.h>

#define DHTPIN 4
#define DHTTYPE DHT11
const int pinRuido = A0;
const int ledVerde = 7;
const int ledAmarillo = 6;
const int ledRojo = 5;

LiquidCrystal lcd(13, 12, 11, 10, 9, 8); 
DHT dht(DHTPIN, DHTTYPE);
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

// --- Time variables ---
unsigned long tiempoAnteriorData = 0;
unsigned long tiempoAnteriorScroll = 0;
const long intervaloData = 8000;  
const int intervaloScroll = 350;   

// --- Initialitation of variables ---
int puntosTotales = 0;
int pT = 0, pH = 0, pL = 0, pR = 0;
String resultSimple = "Wait...";
String listaAlertas = "Iniciando sistema...                "; 
String alertT = "-", alertH = "-", alertL = "-", alertR = "-";
int posicionScroll = 0;

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.print("Cargando...");
  
  pinMode(ledVerde, OUTPUT);
  pinMode(ledAmarillo, OUTPUT);
  pinMode(ledRojo, OUTPUT);
  
  dht.begin();
  if(!tsl.begin()){
    Serial.println("Error: TSL2561 no detectado");
  }
  
  delay(1000);
  lcd.clear();
}

void loop() {
  unsigned long tiempoActual = millis();

  if (tiempoActual - tiempoAnteriorData >= intervaloData || tiempoAnteriorData == 0) {
    tiempoAnteriorData = tiempoActual;

    // Reading the sensors
    float t = dht.readTemperature();       
    float h = dht.readHumidity();          
    sensors_event_t event;
    tsl.getEvent(&event);
    float lux = event.light;               
    int lecturaRuido = analogRead(pinRuido);
    float db = 20 * log10(lecturaRuido + 1) + 20;

    pT = 0; pH = 0; pL = 0; pR = 0;
    alertT = "Common"; alertH = "Common"; alertL = "Common"; alertR = "Common";
    String nuevaLista = ""; 

    // Temperature distribution
    if (t >= 20 && t <= 24) pT = 25;
    else if ((t >= 18 && t < 20) || (t > 24 && t <= 26)) pT = 12;
    if (t < 18) { alertT = "Low_Temp"; nuevaLista += "Low Temp! "; }
    else if (t > 26) { alertT = "High_Temp"; nuevaLista += "High Temp! "; }

    // Humidity distribution
    if (h >= 40 && h <= 60) pH = 25;
    else if ((h >= 30 && h < 40) || (h > 60 && h <= 70)) pH = 12;
    if (h < 30) { alertH = "Low_Hum"; nuevaLista += "Low Hum! "; }
    else if (h > 70) { alertH = "High_Hum"; nuevaLista += "High Hum! "; }

    // Light distribution
    if (lux >= 500 && lux <= 750) pL = 25;
    else if ((lux >= 300 && lux < 500) || (lux > 750 && lux <= 1000)) pL = 12;
    if (lux < 300) { alertL = "Low_Light"; nuevaLista += "Low Light! "; }
    else if (lux > 1000) { alertL = "High_Light"; nuevaLista += "High Light! "; }

    // Noise distribution
    if (db <= 40) pR = 25;
    else if (db > 40 && db <= 50) pR = 12;
    if (db > 50) { alertR = "High_Noise"; nuevaLista += "High Noise! "; }

    puntosTotales = pT + pH + pL + pR;

    
    if (puntosTotales >= 75)      resultSimple = "Great"; 
    else if (puntosTotales >= 50) resultSimple = "Okay "; 
    else                          resultSimple = "Bad   ";


    if (nuevaLista == "") nuevaLista = "Ideal Environment";
    listaAlertas = nuevaLista + "                "; 
    posicionScroll = 0; 

    // LEDs control
    digitalWrite(ledVerde, puntosTotales >= 75);
    digitalWrite(ledAmarillo, (puntosTotales >= 50 && puntosTotales < 75));
    digitalWrite(ledRojo, puntosTotales < 50);

    // Send to Python
    Serial.print("DATA>");
    Serial.print(t); Serial.print(","); Serial.print(h); Serial.print(",");
    Serial.print(lux); Serial.print(","); Serial.print(db); Serial.print(",");
    Serial.print(pT); Serial.print(","); Serial.print(pH); Serial.print(",");
    Serial.print(pL); Serial.print(","); Serial.print(pR); Serial.print(",");
    Serial.print(puntosTotales); Serial.print(","); Serial.print(resultSimple); Serial.print(",");
    Serial.print(alertT); Serial.print(","); Serial.print(alertH); Serial.print(",");
    Serial.print(alertL); Serial.print(","); Serial.println(alertR);
  }

  // LCD ACTUALIZATION ---
  if (tiempoActual - tiempoAnteriorScroll >= intervaloScroll) {
    tiempoAnteriorScroll = tiempoActual;
    
    lcd.setCursor(0, 0);
    lcd.print("Pts:"); 
    lcd.print(puntosTotales);

    if(puntosTotales < 10) lcd.print("  "); else if(puntosTotales < 100) lcd.print(" ");

    lcd.setCursor(8, 0);
    lcd.print("Res:"); 
    lcd.print(resultSimple);

    lcd.setCursor(0, 1);
    lcd.print(listaAlertas.substring(posicionScroll, posicionScroll + 16));

    posicionScroll++;
    if (posicionScroll > (listaAlertas.length() - 16)) {
      posicionScroll = 0; 
    }
  }

}
