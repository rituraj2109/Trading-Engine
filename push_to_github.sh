#!/bin/bash
# Script to push to GitHub

echo "Removing old remote if exists..."
git remote remove origin 2>/dev/null || true

echo "Adding new remote..."
git remote add origin https://github.com/rituraj2109/Trading-Engine-Backend.git

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Your code is now on GitHub."
