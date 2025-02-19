from gtts import gTTS

# Replace the text below with your story
story_text = """
Echoes of the Forgotten

The void stretched infinitely, swallowing all light except for the distant glow of a battle-worn space station, its structure barely holding together against the vast emptiness. The ship's hull shimmered under the faint illumination of distant stars, flickering emergency lights casting distorted, shifting shadows. Inside, the bridge was steeped in a low hum, the faint sound of life support systems punctuated by occasional static. Red strobes pulsed as if mirroring the anxious heartbeat of the crew. Screens flickered erratically, fighting interference from an unknown force. Commander Vega sat at the helm, her fingers hovering over the console as a strange transmission bled through the speakers, broken and desperate.

“Control, we’re picking up a transmission… deep space, uncharted sector.” Her voice was steady, but there was an underlying tension.

Lieutenant Rhys leaned over the console, his fingers dancing over the interface. “It’s faint… but definitely artificial. Someone—or something—is out there.”

Static crackled, the transmission becoming clearer. A whisper, fragile and distorted, slithered into their ears.

“Help me… before they find out.”

Vega’s breath hitched. “Who are you? What’s happening?”

No response. Just the echo of the plea hanging in the air, like a ghost unwilling to move on. The bridge fell into silence, save for the ever-present hum of the station. Vega turned toward the AI interface, her jaw tightening. “AI, analyze.”

The mechanical voice hesitated—a brief, unnatural pause that sent a shiver through the crew. “No known origin. Frequency is… shifting. It’s moving.”

Rhys frowned, his eyes darting across the data stream. “A signal can’t just… move like this. It’s like it’s... alive.”

“That’s not possible… is it?” Vega murmured. Her grip on the armrest tightened. The red emergency lights flickered wildly, painting the bridge in an eerie, pulsing glow.

Then, a new symbol appeared on the screen. It wasn’t static. It writhed, pulsating like it was breathing, shifting erratically as if resisting being deciphered.

Rhys stepped back. “Commander… this isn’t a transmission. It’s a response.”

Vega’s gaze locked onto the screen. “Then let’s respond. Open a channel.”

The AI hesitated before speaking. “Warning… unknown presence detected.”

The screen glitched violently, and suddenly the station shook. A proximity alarm blared.

“Unidentified object detected,” the AI reported. “Distance: 400,000 kilometers. Speed: increasing.”

Vega shot to her feet. “AI, deep scan. Now.”

“Negative. Interference detected. Source: unknown.”

Rhys swore under his breath. “It’s jamming us.”

Ensign Liora whispered, her voice barely audible over the alarms. “What if… it’s already inside?”

The station shuddered again. Outside, a void-black ship materialized, its shape twisting as though space itself rejected its existence. The bridge trembled under a deep, resonant hum—felt in their bones more than heard. The lights dimmed, flickered, then cut out completely.

Darkness.

Then a whisper. Not over the speakers. Not through any known system.

“They see you now.”

Rhys gasped, clutching his head. “I… I can hear it. It’s in my head!”

“Hold your positions,” Vega ordered, her voice firm despite the growing dread in her chest. “Nobody reacts until I say.”

A moment of silence stretched, before a new voice—cold, mechanical, devoid of feeling—pierced through the bridge.

“You should not have answered.”

A thin, silent beam of energy lanced out from the void-black ship, striking the station.

The bridge convulsed. Consoles exploded in showers of sparks. The crew was thrown from their stations, Vega gripping onto the helm as alarms blared. Then—

Nothing.

When Vega’s eyes fluttered open, emergency lights flickered faintly, casting sickly illumination over the bridge. The crew was frozen in place, their eyes wide and vacant.

Rhys gasped, struggling to move. “Something’s… in my mind.”

Liora shook, whispering frantically. “I can feel them watching. They know everything.”

The comm screen flickered erratically. Then—faces. Hundreds of them. Agonized, screaming without sound, their eyes empty voids, their mouths stretched wide in horror.

A voice, hollow and relentless, echoed across the bridge. “Surrender your vessel. The void remembers.”

Vega gritted her teeth. “Not happening.”

Rhys turned toward her, eyes filled with something primal. “Commander… I think they’re inside the ship.”

Beyond the viewport, space itself seemed to fold. A massive, ancient structure emerged, its surface pulsating with alien glyphs—matching the symbol from the transmission. Tendrils of dark energy extended from it, reaching toward the station like grasping fingers.

The final words whispered through the bridge, sealing their fate.

“You have seen too much.”

The ship groaned as unseen forces pulled it toward the monolith. Metallic tendrils latched onto the hull, dragging it deeper into the abyss.

Vega exhaled, her expression hardening. “Then we’ll see more. We fight.”

The void swallowed them whole.



"""

# Set the language for text-to-speech (e.g., 'en' for English)
language = 'en'

# Create a gTTS object with your story text
tts = gTTS(text=story_text, lang=language, slow=False)

# Save the speech audio to an MP3 file
output_file = "output.mp3"
tts.save(output_file)

print(f"Audio file '{output_file}' has been created. You can now import it into CapCut.")
