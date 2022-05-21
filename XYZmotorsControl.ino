#include <AccelStepper.h>
#include <Servo.h>

long receivedXdistance = 0; //distance in mm from the computer
long travelX=0;
long receivedYdistance = 0; //distance in mm from the computer
long travelY=0;
long receivedZdistance = 0; //distance in mm from the computer
long travelZ=0;
int firstCommand =0;
String receivedCommand; //commands from raspberryPi
//int for the movements
String XFirstInt="";
String XSecInt="";
String YFirstInt="";
String YSecInt="";
bool XDone=false;
bool StartX=true;
bool sensDone = false;
String xMovment="";
String yMovment="";
String xMovment1="";
String xMovment2="";
String xMovment3="";
String yMovment1="";
String yMovment2="";
String yMovment3="";
bool ZDone=false;
bool plantOne=false;
int counter =0;
int counterz =0; //change all counterz to flagz=true;

//z movments for pentration 
int Z1 = 4000; //Steps for penetration
int Z2 = 2000; // Steps for penatration 

bool newData, runallowedX, runallowedY,runallowedZ  = false; // booleans for new data from serial, and runallowed flag

const byte interruptPin = 2; //pin for the microswitch using attachInterrupt(); 

// X motor direction Digital 4 (CCW), pulses Digital 5 (CLK)
AccelStepper stepperX(1, 5, 4);
// Y motor direction Digital 6 (CCW), pulses Digital 7 (CLK)
AccelStepper stepperY(1, 7, 6);
// Z motor direction Digital 8 (CCW), pulses Digital 9 (CLK)
AccelStepper stepperZ(1, 9, 8);

// servos setting
int Servo1Pin=10;
int Servo2Pin=11;
Servo sensor1; //wiring color yellow 
Servo sensor2; //wiring color white 


void setup()
{
  pinMode(interruptPin, INPUT_PULLUP); // internal pullup resistor (debouncing)
  attachInterrupt(digitalPinToInterrupt(interruptPin), stopMotor, FALLING); 
  
  Serial.begin(9600); //define baud rate
  Serial.println("Testing 3 inputs XYZ Axis"); //print a message

  //setting up some default values for X motor
  stepperX.setMaxSpeed(8500); //SPEED = Steps / second
  stepperX.setAcceleration(4000); //ACCELERATION = Steps /(second)^2
  stepperX.disableOutputs(); //disable outputs, so the motor is not getting warm (no current)
  stepperX.setCurrentPosition(receivedXdistance);

  //setting up some default values for Y motor
  stepperY.setMaxSpeed(8500); //SPEED = Steps / second
  stepperY.setAcceleration(4000); //ACCELERATION = Steps /(second)^2
  stepperY.disableOutputs(); //disable outputs, so the motor is not getting warm (no current)
  stepperY.setCurrentPosition(0);

 //setting up some default values for Z motor
  stepperZ.setMaxSpeed(8500); //SPEED = Steps / second
  stepperZ.setAcceleration(4000); //ACCELERATION = Steps /(second)^2
  stepperZ.disableOutputs(); //disable outputs, so the motor is not getting warm (no current)
  stepperZ.setCurrentPosition(0);

   //servos setting 
 sensor1.attach(Servo1Pin); //wiring color yellow 
 sensor2.attach(Servo2Pin); //wiring color white 

}

void(* resetFunc) (void) = 0;//declare reset function at address 0

void loop()
{

  
  checkSerialX(); 
  checkSerialY();
  continuousRunZ();
  
}


void continuousRunX() //method for the motor
{
  if (runallowedX == true && StartX == true)
  {
    
    if (abs(stepperX.currentPosition()) < receivedXdistance) //abs() is needed because of the '<' 
    
    {
      stepperX.enableOutputs(); //enable pins
      stepperX.run(); //step the motor (this will step the motor by 1 step at each loop)
    }
    
    else if (abs(stepperX.currentPosition()) > receivedXdistance){
      stepperX.enableOutputs(); //enable pins
      stepperX.run(); //step the motor (this will step the motor by 1 step at each loop)
      
    }
    else  //program enters this part if the required distance is completed
    {
      
      runallowedX = false; //disable running -> the program will not try to enter this if-else anymore
      stepperX.disableOutputs(); // disable power
      stepperX.setCurrentPosition(receivedXdistance);
    
    }
   

    if (stepperX.currentPosition() == receivedXdistance){ //when reach location  
      runallowedX = false; 
      stepperX.disableOutputs();    
      Serial.println("X");
      delay(500);      
      if (receivedXdistance == -36750){ 
        Serial.println('D');
        XDone=false;
        StartX=true;
      }
      else {
        StartX = false;
         XDone =true;
      }
    }


  }
  
  else //program enters this part if the runallowed is FALSE, we do not do anything
  {
    
    return;

  }

  
}

void continuousRunY() //method for the motor
{
  if (runallowedY == true)
  {
    
    if (abs(stepperY.currentPosition()) < receivedYdistance) //abs() is needed because of the '<' 
    
    {
      stepperY.enableOutputs(); //enable pins
      stepperY.run(); //step the motor (this will step the motor by 1 step at each loop)
    }
    
    else if (abs(stepperY.currentPosition()) > receivedYdistance){
      stepperY.enableOutputs(); //enable pins
      stepperY.run(); //step the motor (this will step the motor by 1 step at each loop)
      
    }
    else //program enters this part if the required distance is completed
    {
      
      runallowedY = false; //disable running -> the program will not try to enter this if-else anymore
      stepperY.disableOutputs(); // disable power
      stepperY.setCurrentPosition(receivedYdistance);
    
    }
    
    
    if (stepperY.currentPosition() == receivedYdistance){ //when reach location  
      runallowedY = false; //disable running -> the program will not try to enter this if-else anymore
      stepperY.disableOutputs(); // disable power
      XDone=false;
      
      Serial.println("Y");
      delay(1000);
     if (yMovment != yMovment3 && xMovment != xMovment3 && receivedXdistance == 0 && receivedYdistance == 0){
     Serial.println("Z motor");
     PlantZ();
     }

     if (xMovment == xMovment3 && yMovment == yMovment3){
     XDone=false;
     StartX=true;
     resetFunc();  //call reset
      }

    
   
      
    }


  }

  
  else //program enters this part if the runallowed is FALSE, we do not do anything
  {
    return;

  }
}



void checkSerialX() //method for receiving the commands
{  
  //switch-case would also work, and maybe more elegant
  
  while (Serial.available()>0) //if something comes
  {
    // firstCommand = Serial.readString();
    receivedCommand= Serial.readString();
    if (receivedCommand[0]=='G' || receivedCommand[1]=='G' || receivedCommand[2]=='G' || receivedCommand[3]=='G'){ //
        runallowedX = true; //allow running

          receivedXdistance = -36750; //value for the steps
          Serial.println("Received G");
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          break;
    }

    if (receivedCommand[0]=='S'){
       if (receivedCommand[1]=='N'){ //ON for servo 1
        servo1on();
        delay(1000);}
    else if (receivedCommand[1]=='F'){ //OFF for servo 1
        servo1off();
        delay(1000);}
    else if (receivedCommand[1]=='H'){ //ON for servo 2
        servo2on();
        delay(1000);}
    else if (receivedCommand[1]=='L'){ //OFF for servo 2
        servo2off();
        delay(1000);}}    

  else {
    Serial.println("INSIDE MOTOR LOOP");
    Serial.println(receivedCommand);
   assign(receivedCommand);
    newData = true; //this creates a flag
    sensDone=false;
    break;
  }
  }

  
   if (sensDone == true) //if something comes
  {
     if (xMovment != xMovment3 ){
    newData = true; //this creates a flag
    
     }
     else if (xMovment == xMovment3){
        newData = false;
     }
  }
  if (newData == true) //if we received something (see above)
  {

// demo receivedCommand="(X50,Y40), (X30,Y25), (X0,Y0),"

      
      

      if (sensDone == false) {
        xMovment=xMovment1;
        yMovment=yMovment1;
      }

      if (sensDone == true) {
        if (xMovment==xMovment1){
           xMovment=xMovment2;
           yMovment=yMovment2;          
        }
        else if (xMovment==xMovment2){
           xMovment=xMovment3;
           yMovment=yMovment3;           
        } 
        else if (xMovment==xMovment3) {
           newData=false;
        }  
                 
      }
      
      
      
      
       Serial.println(xMovment);
       
      if (xMovment == "0") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = 0; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
         
       }

      
      if (xMovment == "5") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -2500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
       }

       if (xMovment == "10") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -5000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
       }

       if (xMovment == "15") //this is the measure part
       {
          runallowedX = true; //allow running
          Serial.println(stepperX.currentPosition());
          receivedXdistance = -15000;
          receivedXdistance = -7500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
          
       }

       if (xMovment == "20") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -10000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
      
       }

       if (xMovment == "25") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -12500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
       }

       if (xMovment == "30") //this is the measure part
       {
          runallowedX = true; //allow running
          receivedXdistance = -15000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
         
       }

       if (xMovment == "35") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -17500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
          
       }

       if (xMovment == "40") //this is the measure part
       {
          runallowedX = true; //allow running
          receivedXdistance = -20000;
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
         
       }

       if (xMovment == "45") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -22500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
       }

       if (xMovment == "50") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -25000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
          
       }

       if (xMovment == "55") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -27500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance

       }

       if (xMovment == "60") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -30000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance

       }

       if (xMovment == "65") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -32500; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance
       }

       if (xMovment == "70") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -35000; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance

       }

        if (xMovment == "75") //this is the measure part
       {
          runallowedX = true; //allow running

          receivedXdistance = -37250; //value for the steps
          travelX = receivedXdistance - stepperX.currentPosition();
          stepperX.setMaxSpeed(8000); //set speed
          stepperX.move(travelX); //set distance

       }
       

     
        sensDone=false; 
  }
  //after we went through the above tasks, newData becomes false again, so we are ready to receive new commands again.
 
  newData = false;
  continuousRunX(); //method to handle the X motor
}

void checkSerialY() //method for receiving the commands
{  
  //switch-case would also work, and maybe more elegant
  
//  if (Serial.available() > 0) //if something comes
//  {
//    receivedCommand = Serial.readString(); // this will read the command character
//    newData = true; //this creates a flag
//  }
//
  if (XDone == true) //if we received something (see above)
  {

// demo receivedCommand="(X30,Y40)"

      
    
      Serial.println(yMovment);
//      yMovment = Serial.parseInt();       

      if (yMovment == "0") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = 0; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

      if (yMovment == "5") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -2500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "10") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -5000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "15") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -7500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "20") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -10000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "25") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -12500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "30") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -15000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "35") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -17500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "40") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -20000;
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "45") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -22500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "50") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -25000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "55") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -27500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "60") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -30000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "65") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -32500; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

       if (yMovment == "70") //this is the measure part
       {
          runallowedY = true; //allow running

          receivedYdistance = -35000; //value for the steps
          travelY = receivedYdistance - stepperY.currentPosition();
          stepperY.setMaxSpeed(8000); //set speed
          stepperY.move(travelY); //set distance
       }

    
    XDone = 0;
    
  }
  //after we went through the above tasks, newData becomes false again, so we are ready to receive new commands again.
  continuousRunY(); //method to handle the Y motor
}

void PlantZ() {       
          

          receivedZdistance = Z1; //value for the steps
          travelZ = receivedZdistance - stepperZ.currentPosition();
          stepperZ.setMaxSpeed(8000); //set speed
          stepperZ.move(travelZ); //set distance
          runallowedZ = true; //allow running
          Serial.println(travelZ);
          plantOne=true;
          continuousRunZ();
        
          
}

void Plant2Z() {       
          

          receivedZdistance = Z1 + Z2; //value for the steps
          travelZ = receivedZdistance - stepperZ.currentPosition();
          stepperZ.setMaxSpeed(8000); //set speed
          stepperZ.move(travelZ); //set distance
          runallowedZ = true; //allow running
          Serial.println(travelZ);
          continuousRunZ();
          plantOne=false;
}

void ReturnZ() {       
          
// if (ZDone == true){ //(ZDone == true && counterz ==2)
          receivedZdistance = 0; //value for the steps
          travelZ = receivedZdistance - stepperZ.currentPosition();
          stepperZ.setMaxSpeed(8000); //set speed
          stepperZ.move(travelZ); //set distance
          runallowedZ = true; //allow running
          Serial.println(travelZ);
          continuousRunZ();
          StartX= true;
          checkSerialX();
          Serial.println("return Z");
          
          


// ZDone=false;
}

void continuousRunZ() {
 if (runallowedZ == true)
  {
    
    if (abs(stepperZ.currentPosition()) < receivedZdistance) //abs() is needed because of the '<' 
    
    {
      stepperZ.enableOutputs(); //enable pins
      stepperZ.run(); //step the motor (this will step the motor by 1 step at each loop)
    }
    
      else if (abs(stepperZ.currentPosition()) > receivedZdistance){
      stepperZ.enableOutputs(); //enable pins
      stepperZ.run(); //step the motor (this will step the motor by 1 step at each loop)
      
    }
    
    if (stepperZ.currentPosition() == receivedZdistance){ //when reach location  
      runallowedZ = false; 
      stepperZ.disableOutputs();
      if (counterz == 0){
      if (receivedZdistance == Z1){
          servo1on();
          delay(2000);
          servo1off();
          delay(2000);
//          if (counterz == 0){
//          servo2on();
//          delay(2000);
////          servo2off();
//          }
          Plant2Z(); 
          
          }

        else if (receivedZdistance == Z1 + Z2){
          delay(2000);
          ReturnZ();
          counterz=counterz+1;
        } 
        else if (receivedZdistance == 0){
          Serial.println("Z");
          sensDone = true;
        }

      }
      else if (counterz == 1){
          if (receivedZdistance == Z1){
          servo1on();
          delay(2000);
          servo2on();
          delay(2000);
          ReturnZ();
          counterz=0;         
          }

      
        else if (receivedZdistance == 0){
          Serial.println("Z");
          sensDone = true;
        }
        
      }
        
      
    }

  }
 else //program enters this part if the runallowed is FALSE, we do not do anything
  {
    return;
  }
}


void stopMotor()//function activated by the pressed microswitch
{
  //Stop motor, disable outputs; here we should also reset the numbers if there are any
  runallowedX = false; //disable running
  runallowedY = false;
  runallowedZ = false;
  
      Serial.println("STOP "); //print action
//      stepperX.setCurrentPosition(0); // reset positioN
      stepperX.stop(); //stop motor
      stepperX.disableOutputs(); //disable power
      stepperY.stop(); //stop motor
      stepperY.disableOutputs(); //disable power
      stepperZ.stop(); //stop motor
      stepperZ.disableOutputs(); //disable power
}

void assign( String data) {
 // demo receivedCommand="(X60,Y45), (X25,Y15), (X0,Y0)"
int leng = data.length();
int i=0;

    for (i=0; i< 9; i++) {
       if (data[i] == 'X'){         
        XFirstInt = data[i+1];
        if (data[i+2] !=','){
        XSecInt = data[i+2];
        xMovment1 = XFirstInt + XSecInt;}
        else if (data[i+2] == ','){
         xMovment1 = XFirstInt;}}
         
        if(data[i]=='Y'){
        YFirstInt = data[i+1];
        if (data[i+2] !=')'){
        YSecInt = data[i+2];
        yMovment1 = YFirstInt + YSecInt;}
        else if (data[i+2] ==')'){
        yMovment1 = YFirstInt;} 
        
       }}

       for (i=11; i< 20; i++) {

       if (data[i] == 'X'){         
        XFirstInt = data[i+1];
        if (data[i+2] !=','){
        XSecInt = data[i+2];
        xMovment2 = XFirstInt + XSecInt;}
        else if (data[i+2] == ','){
         xMovment2 = XFirstInt;}}
         
        if(data[i]=='Y'){
        YFirstInt = data[i+1];
        if (data[i+2] !=')'){
        YSecInt = data[i+2];
        yMovment2 = YFirstInt + YSecInt;}
        else if (data[i+2] ==')'){
        yMovment2 = YFirstInt;} 
        
       }}

       for (i=22; i< leng; i++) {
       if (data[i] == 'X'){         
        XFirstInt = data[i+1];
        if (data[i+2] !=','){
        XSecInt = data[i+2];
        xMovment3 = XFirstInt + XSecInt;}
        else if (data[i+2] == ','){
         xMovment3 = XFirstInt;}}
         
        if(data[i]=='Y'){
        YFirstInt = data[i+1];
        if (data[i+2] !=')'){
        YSecInt = data[i+2];
        yMovment3 = YFirstInt + YSecInt;}
        else if (data[i+2] ==')'){
        yMovment3 = YFirstInt;} 
        
       }}
      
         }


     void servo1off(){    
   sensor1.write(92);
   Serial.println("close servo 1");
    }

 void servo1on(){   
   sensor1.write(2);
   Serial.println("open servo 1");
    }

        void servo2off(){  
   sensor2.write(88);
   Serial.println("close servo 2");  
    }

 void servo2on(){
      
   sensor2.write(3);
   Serial.println("open servo 2"); 
    }
