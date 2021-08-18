from elasticbaseline import setup
from wrappertest import test_create

import time

if __name__ == "__main__":
	start = time.time()
	test_create()
	end = time.time()
	print(f"BIL472 System {end-start}")
	start = time.time()
	setup()
	end = time.time()
	print(f"ElasticSearch {end-start}")