准备阶段：

setup_signal_handlers

check_asan_opts

save_cmdline

fix_up_banner

check_if_tty

get_core_count

check_crash_handling

check_cpu_governor

setup_post

setup_shm

init_count_class16

read_testcases

load_auto

pivot_inputs

detect_file_args

check_binary

perform_dry_run

cull_queue

show_init_stats

common_fuzz_stuff //变异完成后的通用处理

write_to_testcase // 变异后的内容写入测试用例

run_target // 运行目标进程

save_if_interesting // 判断是否保存该测试用例

has_new_bits // 是否产生新状态

fuzz_one // 