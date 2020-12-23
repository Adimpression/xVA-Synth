import os
import argparse
# import models
from python import models
import sys
import warnings


import torch
from scipy.io.wavfile import write
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

# from common.text import text_to_sequence
from python.common.text import text_to_sequence
# from waveglow import model as glow
from python import model as glow
# from waveglow.denoiser import Denoiser
from python.denoiser import Denoiser
sys.modules['glow'] = glow




def load_and_setup_model(model_name, parser, checkpoint, device, forward_is_infer=False, ema=True, jitable=False):
    model_parser = models.parse_model_args(model_name, parser, add_help=False)
    model_args, model_unk_args = model_parser.parse_known_args()

    model_config = models.get_model_config(model_name, model_args)
    model = models.get_model(model_name, model_config, device, forward_is_infer=forward_is_infer, jitable=jitable)
    model.eval()

    if checkpoint is not None:
        checkpoint_data = torch.load(checkpoint, map_location="cpu")

        if 'state_dict' in checkpoint_data:
            sd = checkpoint_data['state_dict']
            if any(key.startswith('module.') for key in sd):
                sd = {k.replace('module.', ''): v for k,v in sd.items()}

            TEMP_NUM_SPEAKERS = 5
            symbols_embedding_dim = 384
            model.speaker_emb = nn.Embedding(TEMP_NUM_SPEAKERS, symbols_embedding_dim).to(device)
            if "speaker_emb.weight" not in sd:
                sd["speaker_emb.weight"] = torch.rand((TEMP_NUM_SPEAKERS, 384))

            model.load_state_dict(sd, strict=False)
        if 'model' in checkpoint_data:
            model = checkpoint_data['model']
        else:
            model = checkpoint_data
        print(f'Loaded {model_name}')

    if model_name == "WaveGlow":
        model = model.remove_weightnorm(model)
    model.eval()
    model.device = device
    return model.to(device)



def init (use_gpu):
    torch.backends.cudnn.benchmark = True
    device = torch.device('cuda' if use_gpu else 'cpu')
    parser = argparse.ArgumentParser(description='PyTorch FastPitch Inference', allow_abbrev=False)

    fastpitch = load_and_setup_model('FastPitch', parser, None, device, forward_is_infer=True, jitable=False)
    fastpitch.device = device

    try:
        os.remove("./FASTPITCH_LOADING")
    except:
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wg_ckpt_path = "./resources/app/models/waveglow_256channels_universal_v4.pt"
        if not os.path.exists(wg_ckpt_path):
            wg_ckpt_path = "./models/waveglow_256channels_universal_v4.pt"
        waveglow = load_and_setup_model('WaveGlow', parser, wg_ckpt_path, device, forward_is_infer=True).to(device)
        denoiser = Denoiser(waveglow, device).to(device)

    fastpitch.waveglow = waveglow
    fastpitch.denoiser = denoiser

    return fastpitch


def loadModel (fastpitch, ckpt, n_speakers, device):
    print(f'Loading FastPitch model: {ckpt}')

    checkpoint_data = torch.load(ckpt+".pt", map_location="cpu")
    if 'state_dict' in checkpoint_data:
        checkpoint_data = checkpoint_data['state_dict']

    symbols_embedding_dim = 384
    fastpitch.speaker_emb = nn.Embedding(n_speakers, symbols_embedding_dim).to(device)
    fastpitch.load_state_dict(checkpoint_data, strict=False)

    fastpitch.eval()
    return fastpitch

def infer(user_settings, text, output, fastpitch, speaker_i, pace=1.0, pitch_data=None):

    print(f'Inferring: "{text}" ({len(text)})')

    sigma_infer = 0.9
    stft_hop_length = 256
    sampling_rate = 22050
    denoising_strength = 0.01

    text = torch.LongTensor(text_to_sequence(text, ['english_cleaners']))
    text = pad_sequence([text], batch_first=True).to(fastpitch.device)

    with torch.no_grad():

        mel, mel_lens, dur_pred, pitch_pred = fastpitch.infer_advanced(text, speaker_i=speaker_i, pace=pace, pitch_data=pitch_data)

        audios = fastpitch.waveglow.infer(mel, sigma=sigma_infer)
        audios = fastpitch.denoiser(audios.float(), strength=denoising_strength).squeeze(1)

        for i, audio in enumerate(audios):
            audio = audio[:mel_lens[i].item() * stft_hop_length]
            audio = audio/torch.max(torch.abs(audio))
            write(output, sampling_rate, audio.cpu().numpy())

    [pitch, durations] = [pitch_pred.cpu().detach().numpy()[0], dur_pred.cpu().detach().numpy()[0]]
    pitch_durations_text = ",".join([str(v) for v in pitch])+"\n"+",".join([str(v) for v in durations])
    return pitch_durations_text
