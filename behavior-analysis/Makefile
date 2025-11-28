
CFLAGS = -Wall -Wextra -O2 -g
STRACE_CMD = strace -o trace-logs/trace_$@.log -ttt -xx -y -f -s 65535
STRACE_FILTERS = filters/system_lib.txt filters/signal_hander.txt filters/boring.txt

.PHONY: clean run_bot_1 run_bot_2 analyze_bot_1 analyze_bot_2 run_robothon_web kill_robothon_web trace-logs

run_bot_1: test-code/test_bot_1.py | trace-logs run_robothon_web
	$(STRACE_CMD) python3 $<
	make kill_robothon_web

run_bot_2: test-code/test_bot_2 | trace-logs
	$(STRACE_CMD) ./$<

test-code/test_bot_2: test-code/test_bot_2.c
	$(CC) $(CFLAGS) -o $@ $<

trace-logs/trace_run_bot_1_analyzed.ndjson: trace-logs/trace_run_bot_1.log
	python3 strace_analyzer.py trace-logs/trace_run_bot_1.log > trace-logs/trace_run_bot_1_analyzed.ndjson

trace-logs/trace_run_bot_2_analyzed.ndjson: trace-logs/trace_run_bot_2.log
	python3 strace_analyzer.py trace-logs/trace_run_bot_2.log > trace-logs/trace_run_bot_2_analyzed.ndjson

trace-logs/trace_run_bot_1_filtered.ndjson: trace-logs/trace_run_bot_1_analyzed.ndjson
	cat $< | ./strace_filter_chain.sh $(STRACE_FILTERS) > $@

trace-logs/trace_run_bot_2_filtered.ndjson: trace-logs/trace_run_bot_2_analyzed.ndjson
	cat $< | ./strace_filter_chain.sh $(STRACE_FILTERS) > $@

test-code/ignore_sigterm: test-code/ignore_sigterm.c
	$(CC) $(CFLAGS) -o $@ $<

run_robothon_web: test-code/robothon_web
	./$< &

kill_robothon_web:
	killall -9 robothon_web || true

test-code/robothon_web: test-code/ignore_sigterm
	ln -sf $(realpath $<) $@

trace-logs:
	mkdir -p trace-logs

clean:
	rm -rf trace-logs
	rm -f dataset.csv bot_created_file.txt new_script.sh
	rm -f test-code/test_bot_2 test-code/ignore_sigterm test-code/robothon_web
	make kill_robothon_web
