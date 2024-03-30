dot_path=./example.dot
dot_filename=example.dot
pipeline_method=YOTT #YOTO
num_copies=10
arch_type=ONE-HOP #MESH
output_path=./
num_data=1000

python3 place.py $dot_path $dot_filename $pipeline_method $num_copies $arch_type $output_path $num_data