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

}
