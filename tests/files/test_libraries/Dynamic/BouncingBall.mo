within TestLibrary.Dynamic;
model BouncingBall
  "The 'classic' bouncing ball model with numerical tolerances"
  type Height=Real(unit="m");
  type Velocity=Real(unit="m/s");
  type Acceleration=Real (unit="m/s^2");
  parameter Real e=0.7 "Coefficient of restitution";
  parameter Height h0=1.0 "Initial height";
  parameter Acceleration g=9.81 "Gravity";
  constant Height eps=1e-3 "Small height";
  Boolean done "Flag when to turn off gravity";
  Height h "Height";
  Velocity v(start=0.0, fixed=true) "Velocity";
initial equation
  h = h0;
  done = false;
equation
  v = der(h);
  der(v) = if done then 0 else -g;
  when {h<0,h<-eps} then
    done = h<-eps;
    reinit(v, -e*(if h<-eps then 0 else pre(v)));
  end when;
end BouncingBall;