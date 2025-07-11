.PHONY: build
build:
	cmake -B build -G "Visual Studio 17 2022" -A x64 -DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="89" -DCUDAToolkit_ROOT="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4" -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded -DGGML_METAL_EMBED_LIBRARY=OFF
	cmake --build build --config Release

# 이하 생략