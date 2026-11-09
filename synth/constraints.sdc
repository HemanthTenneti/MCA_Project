# Timing Constraints for Branch Predictor - Arina
# Target: iCE40 HX8K
# Frequency: 25 MHz (40 ns period)

# Define clock
create_clock -name clk -period 40 [get_ports clk]

# Set input delays (assume 5ns setup)
set_input_delay -clock clk 5.0 [get_ports {pc_in actual_next_pc actual_taken reset}]

# Set output delays (assume 5ns clock-to-output)
set_output_delay -clock clk 5.0 [get_ports {predicted_pc predicted_taken flush redirect}]

# Timing budget: 40ns - 5ns(input) - 5ns(output) = 30ns for logic
set_timing_budget -clk clk 30

# Register pipelining constraints
group_path -name pipeline -from [get_pins {predictor*/Q}] -to [get_pins {pipeline_register*/D}]
set_max_delay -path_group pipeline 30

# Critical path analysis
report_timing -delay_type max -max_paths 10

# FPGA resource constraints
set_max_fanout 10
set_max_transition 10

# Report constraints
puts "✓ Constraints applied for 25 MHz operation"
puts "✓ Input delay: 5ns, Output delay: 5ns"
puts "✓ Logic budget: 30ns"
