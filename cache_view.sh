#!/bin/bash

traffic_line -r proxy.node.cache.bytes_total
traffic_line -r proxy.node.cache.bytes_total_mb
traffic_line -r proxy.node.cache.bytes_free
traffic_line -r proxy.node.cache.bytes_free_mb

traffic_line -r proxy.node.cache_total_hits
traffic_line -r proxy.node.cache_total_misses

