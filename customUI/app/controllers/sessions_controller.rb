class SessionsController < ApplicationController
  def new
  end
  
  def create
    user = 'cinnamonhab'
    password = 'chab'
    
    if user == params[:session][:username].downcase && password == params[:session][:password]
        log_in
        render :template => 'main/application'
    else
        flash.now[:danger] = 'Invalid username or password combination'
        render 'new'
    end    
  end
  
  def destroy
        render 'new'
  end
end
