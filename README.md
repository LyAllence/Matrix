# Matrix
# Project:
  This project is to deal with multiplication at big matrix(maybe above one billion)
  And we will use distribute frame
  And the project is base on python 3.6
  And we will have four scripts, two socket server, one client and one script to multiplication matrix

# Script:
  matrix_multiplication_script detail script to deal with matrix
  issued_task_client issued task script
  total_server_service total socket server, send all matrix to clients and accept all response of clients.
  part_server_service part socket server, to accept matrix from total server and use matrix_multiplication_script to
    deal with matrix

# Multiplication:
  per time we will send base matrix to per client, if have other matrix, send to client after the client is finish
  it's work, maybe some client will irq, and it not finish working also will send to other client.
