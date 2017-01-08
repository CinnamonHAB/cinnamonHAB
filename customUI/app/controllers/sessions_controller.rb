class SessionsController < ApplicationController
  def new
  end
  
  def create
    user = 'cinnamonhab'
    password = 'chab'
    
    if user == params[:session][:username].downcase && password == params[:session][:password]
        log_in
        redirect_to 'main#application'
    else
        flash.now[:danger] = 'Invalid username or password combination'
        render 'new'
    end    
  end
  
  def destroy
        log_out
        redirect_to root_url
  end
end
