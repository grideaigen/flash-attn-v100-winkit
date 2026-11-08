import torch
import flash_attn_v100 as fa

torch.manual_seed(0)
dev = "cuda"
B, S, H, D = 2, 256, 8, 64

q = torch.randn(B, S, H, D, device=dev, dtype=torch.half)
k = torch.randn(B, S, H, D, device=dev, dtype=torch.half)
v = torch.randn(B, S, H, D, device=dev, dtype=torch.half)

out, lse = fa.flash_attn_func(q, k, v, causal=True)
torch.cuda.synchronize()
print("forward OK:", out.shape, out.dtype, "| lse:", lse.shape)

q.requires_grad_(True); k.requires_grad_(True); v.requires_grad_(True)
out, _ = fa.flash_attn_func(q, k, v, causal=True)
loss = out.float().pow(2).mean()
loss.backward()
torch.cuda.synchronize()
print("backward OK: loss =", loss.item(),
      "| dq:", tuple(q.grad.shape), "dk:", tuple(k.grad.shape), "dv:", tuple(v.grad.shape))
