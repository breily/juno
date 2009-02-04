#!/usr/bin/env ruby

require 'find'
require 'ftools'

INSTALL_DIR = '/usr/local/lib/python2.5/site-packages/'

puts "** copying juno.py to #{INSTALL_DIR}..."
puts "** overwriting..." if File.exists?(INSTALL_DIR + 'juno.py')
File.copy 'juno.py', INSTALL_DIR

puts "** setup complete"
