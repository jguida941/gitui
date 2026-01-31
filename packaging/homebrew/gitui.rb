class Gitui < Formula
  include Language::Python::Virtualenv

  desc "PySide6 Git UI"
  homepage "https://github.com/jguida941/gitui"
  url "https://github.com/jguida941/gitui/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_ME"

  depends_on "python"
  depends_on "git"

  def install
    venv = virtualenv_create(libexec, "python3")
    venv.pip_install buildpath

    (bin/"gitui").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m app.main "$@"
    EOS
  end

  test do
    system "#{libexec}/bin/python", "-c", "import app"
  end
end
