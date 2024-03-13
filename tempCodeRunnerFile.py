alg = GeneticAlgorithm(configuration)
    alg.run(9999, 0.989)

    get_result(alg.result)

    html_result = HtmlOutput.getResult(alg.result)

    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()

    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    print("\nCompleted in {} secs.\n".format(seconds))
    os.system("open " + temp_file_path)