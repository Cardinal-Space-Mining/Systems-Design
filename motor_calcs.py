import matplotlib.pyplot as plt

torque = 10.354
rpm = 1.184113

max_ratio = 150

motor_torques = [0 for i in range(max_ratio)]
motor_rpms = [0 for i in range(max_ratio)]

for i in range(1, max_ratio):
    motor_torques[i] = torque/i
    motor_rpms[i] = rpm*i

plt.plot(motor_rpms, motor_torques, "o")
plt.plot([0, 5310], [2.43, 0], '-o')
plt.show()


