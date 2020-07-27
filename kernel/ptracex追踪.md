# 起因 

使用ptrace来注入进程 ，detach以后出现了EIP-2的现象，猜测这个eip-2 时为了重新进入系统调用，该篇文章为了验证这个过程。



# 环境

内核版本： 4.10.1

编译， 调试过程参考该目录下其他文档。



# 从系统调用到执行ptrace 分析

## 系统调用



## ptrace过程

### 几个关键函数或者宏

```
/*
写者也可以用它来获得锁，与write_lock不同的是，该宏还同时失效了本地中断。该宏与write_lock_irqsave的不同之处是，它没有保存标志寄存器。
*/
#define write_lock_irq(lock) \
do { \
	local_irq_disable(); \
	preempt_disable(); \
	_raw_write_lock(lock); \
} while (0)
/*

*/
#define write_unlock_irq(lock) \
do { \
	_raw_write_unlock(lock); \
	local_irq_enable(); \
	preempt_enable(); \
} while (0)
/*
将其放会到原父进程之下，并且从ptrace list 列表中移除
*/
void __ptrace_unlink(task_t *child)
{
	if (!child->ptrace)
		BUG();
	child->ptrace = 0;
	if (list_empty(&child->ptrace_list))
		return;
	list_del_init(&child->ptrace_list);
	REMOVE_LINKS(child);
	child->parent = child->real_parent;
	SET_LINKS(child);
}

```

# Detach 过程

```
int ptrace_detach(struct task_struct *child, unsigned int data)
{
	if ((unsigned long) data > _NSIG)
		return	-EIO;

	/* Architecture-specific hardware disable .. */
	ptrace_disable(child);

	/* .. re-parent .. */
	child->exit_code = data;

	write_lock_irq(&tasklist_lock);
	__ptrace_unlink(child);
	/* .. and wake it up. */
	if (child->state != TASK_ZOMBIE)
		wake_up_process(child);
	write_unlock_irq(&tasklist_lock);

	return 0;
}
```

已知了其他函数的作用，我们就把重心放在wake_up_process() 上。wake_up_process 调用了try_to_wake_up() 函数过程。

wake_up_process() 调用try_to_wake_up(),try_wake_up() 函数位于[**kernel/sched.c**](https://elixir.bootlin.com/linux/v2.6.0/source/kernel/sched.c#L664)

```
static int try_to_wake_up(task_t * p, unsigned int state, int sync)
{
	unsigned long flags;
	int success = 0;
	long old_state;
	runqueue_t *rq;

repeat_lock_task:
	//禁止本地中断
	rq = task_rq_lock(p, &flags);
	old_state = p->state;
	if (old_state & state) {
	//如果p->array字段不等于NULL，那么进程已经属于某个运行队列
		if (!p->array) {
			/*
			 * Fast-migrate the task if it's not running or runnable
			 * currently. Do not violate hard affinity.
			 */
			if (unlikely(sync && !task_running(rq, p) &&
				(task_cpu(p) != smp_processor_id()) &&
				cpu_isset(smp_processor_id(), p->cpus_allowed))) {

				set_task_cpu(p, smp_processor_id());
				task_rq_unlock(rq, &flags);
				goto repeat_lock_task;
			}
			
			//进程处于不可中断状态。
			if (old_state == TASK_UNINTERRUPTIBLE){
				rq->nr_uninterruptible--;
				/*
				 * Tasks on involuntary sleep don't earn
				 * sleep_avg beyond just interactive state.
				 */
				p->activated = -1;
			}
			if (sync && (task_cpu(p) == smp_processor_id()))
				__activate_task(p, rq);
			else {
				activate_task(p, rq);
				if (TASK_PREEMPTS_CURR(p, rq))
					resched_task(rq->curr);
			}
			success = 1;
		}
		p->state = TASK_RUNNING;
	}
	task_rq_unlock(rq, &flags);

	return success;
}
```

调试过程中，排除其他函数，定位到resched_task() 函数。

> https://blog.csdn.net/hq815601489/article/details/80009791 Linux系统调用：使用int 0x80
>
> https://blog.csdn.net/weixin_33850890/article/details/92823320 Linux系统调用与ptrace分析
>
> https://www.ibm.com/developerworks/cn/linux/l-synch/part2/index.html Linux 内核的同步机制
>
> http://abcdxyzk.github.io/blog/2015/02/11/kernel-sched-trywakeup/ try_to_wake_up分析

