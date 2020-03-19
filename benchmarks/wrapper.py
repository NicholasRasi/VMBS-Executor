import sh


class Wrapper:
    error_code = 400

    def __init__(self, logger):
        self.logger = logger

    def dd(self, ifile, ofile, bs, count=None, seek=None):
        """
        Wrapper for the GNU dd command.
        """
        try:
            output = sh.dd('if=%s' % ifile, 'of=%s' % ofile,
                           'bs=%s' % bs, 'count=%d' % count, 'conv=fdatasync', _err_to_out=True)
            retcode = output.exit_code
        except Exception as e:
            self.logger.error("exception: " + str(e))
            retcode = self.error_code
            output = e

        return retcode, str(output)

    def curl(self, ofile, url):
        """
        Wrapper for the curl command.
        """
        try:
            output = sh.curl("-o", ofile, "--silent", "--progress-bar",
                             "--write-out", 'Downloaded %{size_download} bytes in %{time_total} sec\n', url)
            retcode = output.exit_code
        except Exception as e:
            self.logger.error("exception: " + str(e))
            retcode = self.error_code
            output = e

        return retcode, str(output)

    def gunicorn(self, workers, dir, file, bg=False):
        """
        Wrapper for the gunicorn command.
        gunicorn -w <num_of_workers> "main:create_app(containers_manager="<containers_manager_host>
        """
        try:
            output = sh.gunicorn("-w", workers, "--chdir", dir, str(file), _bg=bg)
            if bg:
                return output
            retcode = output.exit_code
        except Exception as e:
            self.logger.error("exception: " + str(e))
            retcode = self.error_code
            output = e

        return retcode, str(output)

    def wrk(self, threads, connections, time, url):
        """
        Wrapper for the wrk command.
        https://github.com/wg/wrk
        wrk -t12 -c400 -d30s http://localhost:8081/
        """
        try:
            output = sh.wrk("-t" + str(threads), "-c" + str(connections), "-d" + str(time), str(url))
            retcode = output.exit_code
        except Exception as e:
            self.logger.error("exception: " + str(e))
            retcode = self.error_code
            output = e

        return retcode, str(output)

    def bash(self, exec_file):
        """
        Wrapper for the bash command.
        """
        try:
            output = sh.bash(exec_file)
            retcode = output.exit_code
        except Exception as e:
            self.logger.error("exception: " + str(e))
            retcode = self.error_code
            output = e

        return retcode, str(output)
