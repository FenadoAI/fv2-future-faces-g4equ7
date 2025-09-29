import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Loader2, Heart, Baby, Sparkles, ArrowRight } from 'lucide-react';
import { Textarea } from './ui/textarea';
import { Progress } from './ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const ChildNameGenerator = () => {
  const [step, setStep] = useState(1); // 1: Input, 2: Name Selection, 3: Image Generation, 4: Age Progression
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedNames, setSuggestedNames] = useState([]);
  const [explanation, setExplanation] = useState('');
  const [selectedName, setSelectedName] = useState('');
  const [childImage, setChildImage] = useState('');
  const [ageProgressionImages, setAgeProgressionImages] = useState([]);
  const [progressValue, setProgressValue] = useState(0);

  // Step 1: Generate names
  const handleGenerateNames = async () => {
    if (!description.trim()) {
      toast.error('Please enter a description for the name you want!');
      return;
    }

    setIsLoading(true);
    setProgressValue(25);

    try {
      const response = await axios.post(`${API}/generate-name`, {
        description: description
      });

      if (response.data.success) {
        setSuggestedNames(response.data.suggested_names);
        setExplanation(response.data.explanation);
        setStep(2);
        setProgressValue(50);
        toast.success('Names generated successfully!');
      } else {
        toast.error(response.data.error || 'Failed to generate names');
      }
    } catch (error) {
      console.error('Error generating names:', error);
      toast.error('Failed to generate names. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Generate initial image
  const handleSelectName = async (name) => {
    setSelectedName(name);
    setIsLoading(true);
    setProgressValue(65);

    try {
      const response = await axios.post(`${API}/generate-image`, {
        child_name: name,
        description: description
      });

      if (response.data.success) {
        setChildImage(response.data.image_url);
        setStep(3);
        setProgressValue(80);
        toast.success(`Generated image for ${name}!`);

        // Automatically generate age progression
        setTimeout(() => handleGenerateAgeProgression(name), 1500);
      } else {
        toast.error(response.data.error || 'Failed to generate image');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      toast.error('Failed to generate image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Generate age progression
  const handleGenerateAgeProgression = async (name) => {
    setIsLoading(true);

    try {
      const basePrompt = `A portrait of a happy child named ${name}. ${description}. High quality, professional portrait, soft lighting, warm and friendly expression.`;

      const response = await axios.post(`${API}/generate-age-progression`, {
        base_image_prompt: basePrompt,
        child_name: name,
        ages: [3, 6, 10, 15, 18]
      });

      if (response.data.success) {
        setAgeProgressionImages(response.data.age_progression_images);
        setStep(4);
        setProgressValue(100);
        toast.success('Age progression completed!');
      } else {
        toast.error(response.data.error || 'Failed to generate age progression');
      }
    } catch (error) {
      console.error('Error generating age progression:', error);
      toast.error('Failed to generate age progression.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartOver = () => {
    setStep(1);
    setDescription('');
    setSuggestedNames([]);
    setExplanation('');
    setSelectedName('');
    setChildImage('');
    setAgeProgressionImages([]);
    setProgressValue(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Baby className="h-12 w-12 text-purple-600 mr-3" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Child Name Generator
            </h1>
            <Sparkles className="h-12 w-12 text-pink-600 ml-3" />
          </div>
          <p className="text-gray-600 text-lg mb-6">
            Describe your dream name and watch your future child come to life through different ages
          </p>

          {/* Progress Bar */}
          {step > 1 && (
            <div className="max-w-md mx-auto mb-6">
              <Progress value={progressValue} className="h-2" />
              <p className="text-sm text-gray-500 mt-2">
                Step {step} of 4: {step === 1 ? 'Describe' : step === 2 ? 'Choose Name' : step === 3 ? 'Generate Image' : 'Age Progression'}
              </p>
            </div>
          )}
        </div>

        {/* Step 1: Description Input */}
        {step === 1 && (
          <Card className="max-w-2xl mx-auto shadow-xl border-0 bg-white/80 backdrop-blur">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center text-2xl">
                <Heart className="h-6 w-6 text-red-500 mr-2" />
                Describe Your Dream Name
              </CardTitle>
              <CardDescription className="text-base">
                Tell us what kind of name you're looking for. Be as specific or creative as you want!
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="description" className="text-base font-medium">
                  What kind of name are you looking for?
                </Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="E.g., 'A strong, classic name with European origins' or 'Something modern and unique that sounds musical' or 'A nature-inspired name that's not too common'"
                  className="mt-2 min-h-[120px] text-base"
                  disabled={isLoading}
                />
              </div>
              <div className="text-sm text-gray-500 bg-gray-50 p-4 rounded-lg">
                <strong>Ideas to include:</strong> Gender preference, cultural background, meaning importance,
                sound preferences, length, popularity level, or any special significance you want.
              </div>
            </CardContent>
            <CardFooter>
              <Button
                onClick={handleGenerateNames}
                disabled={isLoading || !description.trim()}
                className="w-full text-lg py-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                ) : (
                  <Sparkles className="h-5 w-5 mr-2" />
                )}
                {isLoading ? 'Generating Names...' : 'Generate Names'}
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* Step 2: Name Selection */}
        {step === 2 && (
          <div className="max-w-4xl mx-auto space-y-6">
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Choose Your Favorite Name</CardTitle>
                <CardDescription>
                  {explanation && (
                    <div className="bg-blue-50 p-4 rounded-lg mt-4">
                      <p className="text-gray-700">{explanation}</p>
                    </div>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {suggestedNames.map((name, index) => (
                    <Button
                      key={index}
                      onClick={() => handleSelectName(name)}
                      disabled={isLoading}
                      variant="outline"
                      className="h-24 text-xl font-semibold hover:bg-gradient-to-r hover:from-purple-100 hover:to-pink-100 hover:border-purple-300 transition-all"
                    >
                      {name}
                    </Button>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleStartOver}>
                  Start Over
                </Button>
                <Button variant="ghost" onClick={handleGenerateNames} disabled={isLoading}>
                  Generate New Names
                </Button>
              </CardFooter>
            </Card>
          </div>
        )}

        {/* Step 3: Image Generation */}
        {step === 3 && (
          <div className="max-w-2xl mx-auto">
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl flex items-center justify-center">
                  <Heart className="h-6 w-6 text-red-500 mr-2" />
                  Meet {selectedName}
                </CardTitle>
                <CardDescription>
                  {isLoading ? 'Generating age progression...' : 'Here\'s how they might look at different ages!'}
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                {childImage && (
                  <div className="mb-6">
                    <img
                      src={childImage}
                      alt={`Portrait of ${selectedName}`}
                      className="w-80 h-80 rounded-2xl mx-auto object-cover shadow-lg"
                    />
                    <Badge variant="secondary" className="mt-4 text-base px-4 py-2">
                      {selectedName} - Age 5
                    </Badge>
                  </div>
                )}

                {isLoading && (
                  <div className="flex items-center justify-center mt-6">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-600 mr-3" />
                    <span className="text-lg">Creating age progression...</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Age Progression Gallery */}
        {step === 4 && (
          <div className="max-w-6xl mx-auto">
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl flex items-center justify-center mb-4">
                  <Heart className="h-8 w-8 text-red-500 mr-3" />
                  {selectedName}'s Journey Through Time
                  <Heart className="h-8 w-8 text-red-500 ml-3" />
                </CardTitle>
                <CardDescription className="text-lg">
                  Watch {selectedName} grow from childhood to adulthood
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
                  {ageProgressionImages.map((ageImage, index) => (
                    <div key={index} className="text-center">
                      <div className="relative group">
                        <img
                          src={ageImage.image_url}
                          alt={`${selectedName} at age ${ageImage.age}`}
                          className="w-full h-64 rounded-xl object-cover shadow-lg transition-transform group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-xl"></div>
                      </div>
                      <Badge variant="default" className="mt-3 text-base px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600">
                        Age {ageImage.age}
                      </Badge>
                    </div>
                  ))}
                </div>

                <div className="text-center bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl">
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">
                    Congratulations! 🎉
                  </h3>
                  <p className="text-gray-600 mb-4">
                    You've discovered {selectedName} and seen their beautiful journey through life.
                    What an amazing name choice!
                  </p>
                </div>
              </CardContent>
              <CardFooter className="flex justify-center space-x-4">
                <Button
                  onClick={handleStartOver}
                  variant="outline"
                  className="px-8 py-3 text-lg"
                >
                  Try Another Name
                </Button>
              </CardFooter>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChildNameGenerator;