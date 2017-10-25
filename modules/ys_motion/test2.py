import sys
sys.path.append("..")

import test1 as test


emp_1 = test.Employee('Sanghee', 'Lee', 50000)

print(emp_1.pay)  # 기존 연봉
emp_1.apply_raise()  # 인상률 적용
print(emp_1.pay)  # 오른 연봉